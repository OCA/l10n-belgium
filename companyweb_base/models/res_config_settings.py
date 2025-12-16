# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cweb_login = fields.Char(related="company_id.cweb_login", readonly=False)
    cweb_password = fields.Char(related="company_id.cweb_password", readonly=False)
    companyweb_followup_enable = fields.Boolean(
        related="company_id.companyweb_followup_enable", readonly=False
    )
    fill_cweb_name = fields.Boolean(related="company_id.fill_cweb_name", readonly=False)
    fill_cweb_commercial_name = fields.Boolean(
        related="company_id.fill_cweb_commercial_name", readonly=False
    )
    fill_cweb_street = fields.Boolean(
        related="company_id.fill_cweb_street", readonly=False
    )
    fill_cweb_zip = fields.Boolean(related="company_id.fill_cweb_zip", readonly=False)
    fill_cweb_city = fields.Boolean(related="company_id.fill_cweb_city", readonly=False)
    fill_cweb_country_id = fields.Boolean(
        related="company_id.fill_cweb_country_id", readonly=False
    )
    fill_cweb_email = fields.Boolean(
        related="company_id.fill_cweb_email", readonly=False
    )
    fill_cweb_website = fields.Boolean(
        related="company_id.fill_cweb_website", readonly=False
    )
    fill_cweb_phone = fields.Boolean(
        related="company_id.fill_cweb_phone", readonly=False
    )
    fill_cweb_vat = fields.Boolean(related="company_id.fill_cweb_vat", readonly=False)
    fill_cweb_registry = fields.Boolean(
        related="company_id.fill_cweb_registry", readonly=False
    )
