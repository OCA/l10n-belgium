# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .account_move import check_bbacomm


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    communication_type = fields.Selection(
        selection_add=[("bba", _("BBA Structured Communication"))],
    )

    @api.constrains("communication", "communication_type")
    def _check_communication(self):
        for rec in self:
            if rec.communication_type == "bba" and not check_bbacomm(rec.communication):
                raise ValidationError(_("Invalid BBA Structured Communication !"))

    def invoice_reference_type2communication_type(self):
        res = super().invoice_reference_type2communication_type()
        res["bba"] = "bba"
        return res
