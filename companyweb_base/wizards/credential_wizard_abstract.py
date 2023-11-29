# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CompanyWebCredentialWizardAbstract(models.AbstractModel):
    _name = "companyweb_base.credential_wizard_abstract"
    _description = "Ask for Companyweb login & password"

    cweb_login = fields.Char("Companyweb Login", required=True)
    cweb_password = fields.Char("Companyweb Password", required=True)

    def _return_action(self):
        return True

    def save_cweb_login_pwd(self):
        """
        save information given in the form to the logged-in user
        """
        self.ensure_one()
        self.env.user.cweb_login = self.cweb_login
        self.env.user.cweb_password = self.cweb_password
        return self._return_action()
