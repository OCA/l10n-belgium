# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        self.ensure_one()
        vals = super(AccountMoveLine, self).\
            _prepare_payment_line_vals(payment_order)
        if 'communication' in vals and self.invoice_id.reference_type == 'bba':
            vals['communication'] =\
                self.invoice_id.reference.replace('+', '').replace('/', '')
        return vals
