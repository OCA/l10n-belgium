import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..models.bpost_address import BpostAddress

# Copyright 2023 ACSONE SA/NV


class BpostAddressValidationWizard(models.TransientModel):
    _name = "bpost.address.validation.wizard"

    partner_id = fields.Many2one("res.partner", readonly=True)
    response_address = fields.Json(compute="_compute_response_address")
    is_valid = fields.Boolean(compute="_compute_is_valid_address")
    bad_address = fields.Boolean()
    warning_message = fields.Char(readonly=True)
    suggest_changes = fields.Char(readonly=True)
    bpost_address = fields.Json(compute="_compute_bpost_address")

    @api.depends("partner_id")
    def _compute_response_address(self):
        for rec in self:
            partner = rec.partner_id
            if partner.country_id.code == "BE":
                # This is the JSON that should be sent as input to the API.
                playload = {
                    "ValidateAddressesRequest": {
                        "AddressToValidateList": {
                            "AddressToValidate": [
                                {
                                    "@id": "1",
                                    "PostalAddress": {
                                        "DeliveryPointLocation": {
                                            "UnstructuredDeliveryPointLocation": partner.street
                                        },
                                        "PostalCodeMunicipality": {
                                            "UnstructuredPostalCodeMunicipality": partner.zip
                                            + " "
                                            + partner.city
                                        },
                                    },
                                }
                            ]
                        },
                        "ValidateAddressOptions": {
                            "IncludeFormatting": "true",
                            "IncludeSuggestions": "true",
                            "IncludeSubmittedAddress": "true",
                            "IncludeListOfBoxes": "true",
                            "IncludeNumberOfBoxes": "true",
                            "IncludeDefaultGeoLocation": "true",
                            "IncludeDefaultGeoLocationForBoxes": "true",
                        },
                    }
                }
                response = requests.post(
                    "https://webservices-pub.bpost.be/ws/"
                    + "ExternalMailingAddressProofingCSREST_v1/address/validateAddresses",
                    json=playload,
                    timeout=10,
                    headers={"content-type": "application/json"},
                )
                if response.ok:
                    rec.response_address = response.json()
                else:
                    rec.response_address = {}
                    raise UserError(
                        _("An error occurred when fetching data from bpost API.")
                    )
            else:
                rec.response_address = {}

    @api.depends("response_address")
    def _compute_bpost_address(self):
        for rec in self:
            # Transform the result into a BpostAddress object.
            rec.bpost_address = BpostAddress(rec.response_address).toJson()

    @api.depends("bpost_address")
    def _compute_is_valid_address(self):
        for rec in self:
            if rec.bpost_address:
                if "error" in rec.bpost_address:
                    if (
                        "street_name" in rec.bpost_address
                        and "postal_code" in rec.bpost_address
                        and "municipality_name" in rec.bpost_address
                        and "street_number" in rec.bpost_address
                    ):
                        rec.warning_message = _(
                            "An error has been detected in the given address. "
                            + "Would you like to keep the suggest change ?"
                        )
                        changes = "{} {} {}, {}".format(
                            rec.bpost_address["street_name"],
                            rec.bpost_address["street_number"],
                            rec.bpost_address["postal_code"],
                            rec.bpost_address["municipality_name"],
                        )

                        rec.suggest_changes = changes
                        rec.bad_address = False
                        rec.is_valid = False
                    else:
                        rec.warning_message = _(
                            "The given address is not complete or the address cannot be found"
                        )
                        rec.bad_address = True
                        rec.is_valid = False
                else:
                    rec.is_valid = True
            else:
                rec.is_valid = True

    def apply_changes(self):
        for rec in self:
            rec.is_valid = True
            partner = rec.partner_id
            if (
                "street_name" in rec.bpost_address
                and "postal_code" in rec.bpost_address
                and "municipality_name" in rec.bpost_address
                and "street_number" in rec.bpost_address
            ):
                partner.street = (
                    rec.bpost_address["street_name"]
                    + " "
                    + rec.bpost_address["street_number"]
                )
                partner.city = rec.bpost_address["municipality_name"]
                partner.zip = rec.bpost_address["postal_code"]
                rec.suggest_changes = ""
                rec.bad_address = False
