# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from odoo.addons.base.models import res_users

res_users.USER_PRIVATE_FIELDS.append("cweb_login")
res_users.USER_PRIVATE_FIELDS.append("cweb_password")


class CompanyWebUser(models.Model):
    _inherit = "res.users"

    # If empty, the user will be prompted for these fields via a wizard.
    cweb_login = fields.Char("Companyweb Login")
    cweb_password = fields.Char("Companyweb Password")
