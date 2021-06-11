# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class CompanyWebCredentialWizardPayment(models.TransientModel):

    _name = "companyweb_payment_info.credential_wizard_payment"
    _description = "Ask for Companyweb login & password"
    _inherit = ["companyweb_base.credential_wizard_abstract"]

    def _return_action(self):
        return (
            self.env["companyweb_payment_info.payment_info_wizard"]
            .create({})
            .payment_info_entry_point()
        )
