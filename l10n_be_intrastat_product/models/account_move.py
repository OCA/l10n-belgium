# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("date", "intrastat_transaction_id")
    def _check_intrastat_transaction_id(self):
        for rec in self:
            if rec.company_id.country_id.code != "BE":
                continue
            if not rec.intrastat_transaction_id:
                continue
            msg1 = _("Select a 1 digit intrastat transaction code.")
            msg2 = _("Select a 2 digit intrastat transaction code.")
            if int(rec.intrastat_transaction_id.code) >= 10 and rec.date.year <= 2021:
                raise UserError(msg1)
            elif int(rec.intrastat_transaction_id.code) < 10 and rec.date.year > 2021:
                raise UserError(msg2)
