# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import json
import logging


import requests

from odoo import _, exceptions
from odoo.tools import ustr


_logger = logging.getLogger(__name__)


class CodaboxAPI(object):
    def __init__(self, odoo_env):
        self.env = odoo_env
        IrConfig = self.env["ir.config_parameter"]
        self.prod = IrConfig.get_param("codabox.api.prod.environment")
        if self.prod:
            self.url = "https://api.codabox.com/v2"
        else:
            self.url = "https://sandbox-api.codabox.com/v2"
        key = IrConfig.get_param("codabox.api.key")
        if not key:
            raise exceptions.Warning(_("No CodaBox software key defined."))
        self.headers = {"X-Software-Company": str(key)}
        username = IrConfig.get_param("codabox.api.username", "")
        password = IrConfig.get_param("codabox.api.password", "")
        self._auth = requests.auth.HTTPBasicAuth(str(username), str(password))

    def get_auth(self):
        """
        Checks if the password and the username are correctly filled
        :return: The request auth parameter
        """
        if not self._auth.username:
            raise exceptions.Warning(
                _(
                    "No CodaBox username defined. Please enter your CodaBox "
                    "credentials first"
                )
            )
        if not self._auth.password:
            raise exceptions.Warning(
                _(
                    "No CodaBox password defined. Please enter your CodaBox "
                    "credentials first"
                )
            )
        return self._auth

    @staticmethod
    def http_error_message(response, error_msg):
        """
        :param response: HTTP response of the request
        :param error_msg: Custom error message to display to the user
        :return: Message with
        """
        return "{}. Reason:\n{} ({})".format(
            error_msg, response.json().get("detail"), response.status_code
        )

    def get_credentials(self, token):
        """
        Sends a request to the CodaBox API to retrieve the credentials with the
        one time token
        :param token: One time token used to retrieve the credentials
        """
        url = "{}/get-credentials/{}".format(self.url, token)

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            IrConfig = self.env["ir.config_parameter"]
            response_data = response.json()
            IrConfig.set_param("codabox.api.username", response_data.get("username"))
            IrConfig.set_param("codabox.api.password", response_data.get("password"))
        else:
            msg = self.http_error_message(
                response,
                "Could not retrieve credentials, "
                "please remember that a token can only be used once",
            )
            raise exceptions.Warning(msg)

    def request_token(self, vat):
        """
        Sends a request to get a new token sent to the client's contact email
        address
        """
        url = "%s/request-access-token/invoicing-software/" % self.url
        self.headers.update({"Content-Type": "application/json"})
        data = json.dumps({"vat": vat})
        response = requests.post(url, headers=self.headers, data=data)
        if response.status_code == 201:
            return True
        else:
            msg = self.http_error_message(response, "Could not request a token")
            raise exceptions.Warning(msg)

    def get_feed_list(self):
        """
        Gets the document feed list available for the user
        """
        url = "%s/delivery/pod-client/" % self.url
        response = requests.get(url, headers=self.headers, auth=self.get_auth())
        if response.status_code == 200:
            data = response.json()
            feed_clients = data.get("feed_clients")
            for feed in feed_clients:
                CodaboxFeed = self.env["codabox.feed"]
                if not CodaboxFeed.search([("identifier", "=", feed.get("id"))]):
                    CodaboxFeed.create(
                        {
                            "identifier": feed.get("id"),
                            "name": feed.get("client_name"),
                            "client_uuid": feed.get("client_id"),
                            "client_code_uuid": feed.get("client_code"),
                            "fiduciary_uuid": feed.get("fiduciary_id"),
                        }
                    )
        else:
            msg = self.http_error_message(response, "Could not get the feed list")
            _logger.error(msg)

    def fetch_feed_entries(self, feed_id):
        """
        Get the list of available documents for the selected feed
        :param feed_id: API identifier of the feed
        """
        url = "%s/delivery/feed/%d" % (self.url, feed_id)
        response = requests.get(url, headers=self.headers, auth=self.get_auth())
        if response.status_code == 200:
            data = response.json()
            FeedEntry = self.env["codabox.feed.entry"]
            feed = self.env["codabox.feed"].search([("identifier", "=", feed_id)])
            for entry in data.get("feed_entries"):
                index_uuid = entry.get("feed_index")
                if not FeedEntry.search([("index_uuid", "=", index_uuid)]):
                    if entry.get("document_model") == "coda":
                        self.create_coda_entry(entry, feed.id)
                if self.prod:
                    self.update_feed_offset(feed_id, index_uuid)
        else:
            msg = self.http_error_message(response, "Could not fetch feed entries")
            _logger.error(msg)

    def create_coda_entry(self, entry, feed_id):
        """
        Creates the Coda entry in Odoo based on the JSON data retrieved from
        CODA box and retrieves the CODA file
        :param entry: JSON data of the CODA entry
        :param feed_id: Odoo id of the feed
        """
        metadata = entry.get("metadata")
        coda_entry = self.env["codabox.coda.entry"].create(
            {
                "feed_id": feed_id,
                "index_uuid": entry.get("feed_index"),
                "document_model": entry.get("document_model"),
                "movement_count": metadata.get("movement_count"),
                "first_statement_number": metadata.get("first_statement_number"),
                "last_statement_number": metadata.get("last_statement_number"),
                "date": metadata.get("new_balance_date"),
                "iban": metadata.get("iban"),
                "bic": metadata.get("bank_id"),
                "currency": metadata.get("currency"),
            }
        )
        self.get_document(coda_entry, "cod")
        try:
            coda_entry.import_statement()
        except Exception as excep:
            _logger.error(ustr(excep))

    def get_document(self, entry, file_format="xml"):
        """
        Downloads the document from the CodaBox API in the specified format
        :param entry: Feed entry object for which we retrieve the document
        :param file_format: xml or cod; Format of the document
        """
        url = "{}/delivery/download/{}/{}".format(
            self.url, entry.index_uuid, file_format
        )
        response = requests.get(url, headers=self.headers, auth=self.get_auth())

        if response.status_code == 200:
            encoded_data = base64.b64encode(response.text.encode("ascii"))
            if file_format == "xml":
                entry.xml_file = encoded_data
            elif file_format == "cod":
                entry.coda_file = encoded_data
        else:
            msg = self.http_error_message(response,
                                          "Could not retrieve document")
            if self.env.context.get("cron"):
                _logger.error(msg)
            else:
                raise exceptions.Warning(msg)

    def update_feed_offset(self, feed_id, index_uuid):
        """
        Updates the CodaBox feed offset of the specified feed
        :param feed_id: CodaBox id of the feed to update
        :param index_uuid: Uuid of the feed entry to mark as done
        """
        # Check that there is a recorded entry before updating codabox feed
        if self.env["codabox.feed.entry"].search([("index_uuid", "=", index_uuid)]):
            url = "%s/delivery/feed/%d/" % (self.url, feed_id)
            headers = self.headers
            headers.update({"Content-Type": "application/json"})
            data = json.dumps({"feed_offset": index_uuid})
            response = requests.put(
                url, data=data, headers=self.headers, auth=self.get_auth()
            )
            if response.status_code != 200:
                msg = self.http_error_message(response, "Could not update offset")
                _logger.exception(msg)
