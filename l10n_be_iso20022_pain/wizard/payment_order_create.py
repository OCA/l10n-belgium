# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Stéphane Bidoul
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    @api.model
    def _prepare_payment_line(self, payment, line):
        res = super(PaymentOrderCreate, self).\
            _prepare_payment_line(payment, line)
        # the bba reference_type is defined in l10n_be_invoice_bba
        if line.invoice and line.invoice.reference_type == 'bba':
            res['state'] = 'structured'
            res['struct_communication_type'] = 'BBA'
            res['communication'] = line.invoice.reference.\
                replace('+', '').\
                replace('/', '')
        return res
