# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
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

from openerp.osv import fields, orm


class account_companyweb_wizard(orm.TransientModel):

    _name = 'account.companyweb.wizard'
    _columns = {
        'vat_number': fields.text('VAT number', readonly=True),
        'name': fields.text('Name', readonly=True),
        'jur_form': fields.text('Juridical Form', readonly=True),
        'street': fields.text('Address', readonly=True),
        'zip': fields.text('Postal code', readonly=True),
        'city': fields.text('City', readonly=True),
        'creditLimit': fields.float('Credit limit', readonly=True),
        'startDate': fields.date('Start date', readonly=True),
        'endDate': fields.date('End date', readonly=True),
        'image': fields.binary('Health barometer', readonly=True),
        'warnings': fields.text('Warnings', readonly=True),
        'url': fields.char('Detailed Report', readonly=True),
        'vat_liable': fields.boolean("Subject to VAT", readonly=True),
        'balance_year': fields.text("Balance year", readonly=True),
        'equityCapital': fields.float('Equity Capital', readonly=True),
        'addedValue': fields.float('Gross Margin (+/-)', readonly=True),
        'turnover': fields.float('Turnover', readonly=True),
        'result': fields.float('Fiscal Year Profit/Loss (+/-)', readonly=True),
    }

    def get_update_values(self, cr, uid, ids, wizard, context=None):
        """ This method is designed to be inherited to add some field to
            update on res.partner"""
        return {'name': wizard.name,
                'is_company': True,
                'street': wizard.street,
                'city': wizard.city,
                'zip': wizard.zip,
                'credit_limit': wizard.creditLimit,
                }

    def update_information(self, cr, uid, ids, context=None):
        res_partner_model = self.pool['res.partner']
        partner_id = context['active_id']
        this = self.browse(cr, uid, ids, context=context)[0]
        update_values = self.get_update_values(cr, uid, ids, this,
                                               context=context)
        res_partner_model.write(cr, uid, [partner_id], update_values,
                                context=context)
        return True
