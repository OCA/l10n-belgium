# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import api, models


def check_bbacomm(val):
    supported_chars = "0-9+*/ "
    pattern = re.compile("[^" + supported_chars + "]")
    if pattern.findall(val or ""):
        return False
    bbacomm = re.sub(r"\D", "", val or "")
    if len(bbacomm) == 12:
        base = int(bbacomm[:10])
        mod = base % 97 or 97
        if mod == int(bbacomm[-2:]):
            return True
    return False


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("reference_type", "ref")
    def _check_communication(self):
        for rec in self:
            if (
                rec.journal_id.invoice_reference_model == "be"
                and rec.journal_id.invoice_reference_type == "invoice"
                and rec.reference_type == "structured"
            ):
                return check_bbacomm(rec.ref)

    def _get_invoice_reference_be_invoice(self):
        self.ensure_one()
        if self.reference_type == "none":
            return ""
        return super()._get_invoice_reference_be_invoice()
