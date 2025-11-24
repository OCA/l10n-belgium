# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CompanyWebUser(models.Model):
    _inherit = "res.users"

    # If empty, the user will be prompted for these fields via a wizard.
    # Odoo 19.0: Use groups=fields.NO_ACCESS instead of USER_PRIVATE_FIELDS
    cweb_login = fields.Char("Companyweb Login", groups=fields.NO_ACCESS)
    cweb_password = fields.Char("Companyweb Password", groups=fields.NO_ACCESS)
