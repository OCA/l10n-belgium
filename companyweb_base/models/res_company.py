# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cweb_login = fields.Char("Companyweb Login", groups="companyweb_base.cweb_download")
    cweb_password = fields.Char(
        "Companyweb Password", groups="companyweb_base.cweb_download"
    )
    companyweb_followup_enable = fields.Boolean("Enable Contact Data Followup")

    fill_cweb_name = fields.Boolean(default=True)
    fill_cweb_commercial_name = fields.Boolean(default=True)
    fill_cweb_street = fields.Boolean(default=True)
    fill_cweb_zip = fields.Boolean(default=True)
    fill_cweb_city = fields.Boolean(default=True)
    fill_cweb_country_id = fields.Boolean(default=True)
    fill_cweb_email = fields.Boolean(default=True)
    fill_cweb_website = fields.Boolean(default=True)
    fill_cweb_phone = fields.Boolean(default=True)
    fill_cweb_vat = fields.Boolean(default=True)
    fill_cweb_registry = fields.Boolean(default=True)

    _cweb_login_unique = models.Constraint(
        "UNIQUE(cweb_login)",
        "These credentials are already in use, please contact Companyweb.",
    )
