# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def create(self, cr, uid, vals, context=None):
        if vals.get('state') != 'iban':
            env = api.Environment(cr, uid, context)
            bank = env['res.bank'].browse(vals.get('bank'))
            if bank.country == env.ref('base.be') and bank.bic and bank.code:
                vals['state'] = 'iban'
                vals['acc_number'] = \
                    env['res.bank'].bban2iban('be', vals['acc_number'])
        return super(ResPartnerBank, self).create(cr, uid, vals, context)
