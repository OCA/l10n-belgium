# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError

from .account_move import check_bbacomm


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    @api.constrains("order_id", "communication", "communication_type")
    def _check_communication(self):
        for rec in self:
            if (
                rec.order_id.journal_id.invoice_reference_type == "invoice"
                and rec.order_id.journal_id.invoice_reference_model == "be"
                and rec.communication_type == "structured"
                and not check_bbacomm(rec.communication)
            ):
                raise ValidationError(_("Invalid BBA Structured Communication !"))
