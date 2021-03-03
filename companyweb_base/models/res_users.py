# Copyright 2021-2023 ACSONE SA/NV
from odoo import fields, models

from odoo.addons.base.models import res_users

res_users.USER_PRIVATE_FIELDS.append("cweb_login")
res_users.USER_PRIVATE_FIELDS.append("cweb_password")


class CompanyWebUser(models.Model):
    _inherit = "res.users"

    # If empty, the user will be prompted for these fields via a wizard.
    cweb_login = fields.Char("Companyweb Login")
    cweb_password = fields.Char("Companyweb Password")
