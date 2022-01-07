# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from requests.exceptions import ConnectionError as ConError

from odoo import exceptions, fields, models
from odoo.tools import ustr

from odoo.addons.codabox.tools.codabox_api import CodaboxAPI


class CodaboxMessageWizard(models.TransientModel):
    _name = "codabox.message.wizard"
    _description = "coda box message wizard"

    message = fields.Char("Message", readonly=True)


class CodaboxCredentialsWizard(models.TransientModel):
    _name = "codabox.credentials.wizard"
    _description = "coda box credentials wizard"

    token = fields.Char("Token")
    vat = fields.Char("VAT Number")

    def retrieve_credentials(self):
        """
        Sends a request to the CodaBox API to retrieve the credentials with the
        one time token
        """
        self.ensure_one()
        codabox_api = CodaboxAPI(self.env)
        codabox_api.get_credentials(self.token)
        # Reload the config page with the updated parameters
        return {
            "type": "ir.actions.act_window",
            "view_id": self.env.ref("codabox.codabox_config_settings_form").id,
            "name": "Retrieve Credentials",
            "target": "inline",
            "res_model": "res.config.settings",
            "view_type": "form",
            "view_mode": "form",
        }

    def request_token(self):
        """
        Sends a request to get a new token sent to the client's contact email
        address
        """
        self.ensure_one()
        codabox_api = CodaboxAPI(self.env)
        try:
            codabox_api.request_token(self.vat)

            return {
                "type": "ir.actions.act_window",
                "view_id": self.env.ref("codabox.codabox_message_wizard_form").id,
                "name": "Token Request Successful",
                "target": "new",
                "res_model": "codabox.message.wizard",
                "view_type": "form",
                "view_mode": "form",
                "context": {
                    "default_message": "CodaBox sent an email to your contact "
                    "address with the one time token"
                },
            }
        except ConError as error:
            return {
                "type": "ir.actions.act_window",
                "view_id": self.env.ref("codabox.codabox_message_wizard_form").id,
                "name": "Token Request failed",
                "target": "new",
                "res_model": "codabox.message.wizard",
                "view_type": "form",
                "view_mode": "form",
                "context": {
                    "default_message": "An error occurred while trying to contact "
                    "Codabox API to request the token\n"
                    "Please check your internet connection\n"
                    "[%s]" % ustr(error)
                },
            }
        except exceptions.Warning:
            return {
                "type": "ir.actions.act_window",
                "view_id": self.env.ref("codabox.codabox_message_wizard_form").id,
                "name": "Token Request failed",
                "target": "new",
                "res_model": "codabox.message.wizard",
                "view_type": "form",
                "view_mode": "form",
                "context": {
                    "default_message": "An error occurred while trying to contact "
                    "Codabox API to request the token\n"
                    "Please make sure that you provided the "
                    "right data"
                },
            }
