# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class CompanyWebCredentialWizardBase(models.TransientModel):
    _name = "companyweb_base.credential_wizard_base"
    _description = "Ask for Companyweb login & password"
    _inherit = ["companyweb_base.credential_wizard_abstract"]

    def _return_action(self):
        return (
            self.env["res.partner"]
            .browse(self.env.context["active_id"])
            .cweb_button_enhance()
        )
