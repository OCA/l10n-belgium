# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, exceptions, fields, models

from ..cweb_const import (
    ALLOWED_COUNTRY_CODES,
    ALLOWED_COUNTRY_SELECTION,
    COUNTRY_CODE_BELGIUM,
    SEARCH_RESULT_KEYS,
)


class CompanywebBaseSearchWizard(models.TransientModel):
    _name = "companyweb.search.wizard"
    _description = "Companyweb Search Wizard"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")

    vat = fields.Char("VAT")
    company_registry = fields.Char("Company ID")
    search_term = fields.Char()
    zip = fields.Char("ZIP Code")
    city = fields.Char()
    country_code = fields.Selection(
        ALLOWED_COUNTRY_SELECTION,
        "Country",
    )

    display_search_button = fields.Boolean(default=True, readonly=True)
    line_ids = fields.One2many(
        "companyweb.search.wizard.line", "wizard_id", "Search Results"
    )

    @api.onchange(
        "partner_id",
        "vat",
        "company_registry",
        "search_term",
        "zip",
        "city",
        "country_code",
    )
    def _onchange_search_terms(self):
        self.ensure_one()
        self.display_search_button = True

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if "partner_id" in result:
            partner = self.env["res.partner"].browse(result["partner_id"])
            result.update(
                {
                    "search_term": partner.name,
                    "vat": partner.vat,
                    "company_registry": partner.company_registry,
                    "zip": partner.zip,
                    "city": partner.city,
                    "country_code": (code := partner.country_id.code)
                    in ALLOWED_COUNTRY_CODES
                    and code
                    or COUNTRY_CODE_BELGIUM,
                }
            )
        return result

    def open(self):
        self.ensure_one()
        action = self.get_formview_action()
        action.update(
            {
                "name": "Search Companyweb",
                "target": "new",
            }
        )
        return action

    def companyweb_search(self):
        """
        Get search results and create wizard lines
        """
        self.ensure_one()
        if not self.partner_id._cweb_ensure_credentials():
            return self.partner_id._cweb_call_wizard_credentials()
        args = {
            "vat": self.vat,
            "registry": self.company_registry,
            "search": self.search_term,
            "zip": self.zip,
            "city": self.city,
            "country_code": self.country_code,
        }
        error, results = self.partner_id._cweb_call_get(args)
        if error:
            raise exceptions.ValidationError(error)
        line_vals = []
        for item in results:
            line_vals.append(
                {key: item.get(value) for key, value in SEARCH_RESULT_KEYS.items()}
            )
        self.line_ids = [Command.clear()] + [Command.create(val) for val in line_vals]
        self.display_search_button = False
        return self.open()
