# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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

    reference_type = fields.Selection(
        selection_add=[("bba", "BBA Structured Communication")]
    )

    @api.constrains("reference_type", "ref")
    def _check_communication(self):
        for rec in self:
            if rec.reference_type == "bba":
                return check_bbacomm(rec.ref)
        return True

    @api.model
    def _update_reference_vals(self, vals):
        reference = vals.get("ref", False)
        reference_type = vals.get("reference_type", False)
        if reference_type == "bba":
            if not reference:
                raise UserError(
                    _(
                        "Empty BBA Structured Communication! "
                        "Please fill in a unique BBA Structured Communication."
                    )
                )
            reference = re.sub(r"\D", "", reference)
            vals["ref"] = (
                "+++"
                + reference[0:3]
                + "/"
                + reference[3:7]
                + "/"
                + reference[7:]
                + "+++"
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_reference_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._update_reference_vals(vals)
        return super().write(vals)
