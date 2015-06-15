# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Author: Adrien Peiffer
#    Contributor: Jacques-Etienne Baudoux <je@bcim.be> BCIM sprl
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    Copyright (c) 2015 BCIM sprl (http://www.bcim.be)
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

import logging

from openerp import models, fields, api, _
from openerp.exceptions import Warning

from .companyweb_rest import companyweb_getcompanydata

logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    cweb_lastupdate = fields.Datetime('Last update', readonly=True)

    cweb_name = fields.Char('Name', readonly=True)
    cweb_jur_form = fields.Char('Juridical Form', readonly=True)
    cweb_street = fields.Char('Address', readonly=True)
    cweb_zip = fields.Char('Postal code', readonly=True)
    cweb_city = fields.Char('City', readonly=True)
    cweb_creditLimit = fields.Float('Credit limit', readonly=True)
    cweb_startDate = fields.Date('Start date', readonly=True)
    cweb_endDate = fields.Date('End date', readonly=True)
    cweb_score = fields.Char('Score', readonly=True)
    cweb_image = fields.Binary('Health barometer', readonly=True)
    cweb_warnings = fields.Text('Warnings', readonly=True)
    cweb_url = fields.Char('Detailed Report', readonly=True)
    cweb_vat_liable = fields.Boolean("Subject to VAT", readonly=True)
    cweb_balance_year = fields.Char("Balance Year", readonly=True)
    cweb_equityCapital = fields.Float('Equity Capital', readonly=True)
    cweb_addedValue = fields.Float('Gross Margin (+/-)', readonly=True)
    cweb_turnover = fields.Float('Turnover', readonly=True)
    cweb_result = fields.Float('Fiscal Year Profit/Loss (+/-)', readonly=True)
    cweb_employees = fields.Float('Number of Employees', readonly=True)
    cweb_prefLang = fields.Char('Preferred Language', readonly=True)

    def _companyweb_information(self, vat_number):
        login = self.pool['ir.config_parameter'].get_param(
            self._cr, self._uid, 'companyweb.login', False)
        pswd = self.pool['ir.config_parameter'].get_param(
            self._cr, self._uid, 'companyweb.pswd', False)

        params = {
            'login': login,
            'pswd': pswd,
            'vat': vat_number,
            }

        if self._context.get('lang', '').startswith('fr'):
            params['lang'] = 1
        elif self._context.get('lang', '').startswith('nl'):
            params['lang'] = 2

        data = companyweb_getcompanydata(**params)

        values = {'cweb_lastupdate': fields.Datetime.now()}
        for k, v in data.iteritems():
            key = "cweb_%s" % k
            if key in self._all_columns:
                values[key] = v
        return values

    @api.one
    def button_cweb_fetch(self, force_update=True):
        self._cweb_refresh(force_update=True)

    @api.one
    def button_cweb_refresh(self, force_update=False):
        self._cweb_refresh(force_update=False)

    @api.one
    def _cweb_refresh(self, force_update=False):
        vat = self.vat or self.name

        vat_country = vat[:2].lower()
        vat_number = vat[2:].replace(' ', '')

        if vat_country == "be":
            try:
                int(vat_number)
                # IMP: call check vat number before
            except ValueError:
                raise Warning(_("This company has no VAT number"))
            values = self._companyweb_information(vat_number)
            if force_update:
                values.update(self._companyweb_values_to_update(values))
            if not self.vat:
                values['vat'] = vat
            self.write(values)
            return

        raise Warning(_("Companyweb is only available for companies with a Belgian VAT number"))

    def _companyweb_values_to_update(self, record):
        """ This method is designed to be inherited to add some field to
            update on res.partner"""
        res = {
            'name': record['cweb_name'],
            'is_company': True,
            'street': record['cweb_street'],
            'city': record['cweb_city'],
            'zip': record['cweb_zip'],
            'credit_limit': record['cweb_creditLimit'],
            }
        if record['cweb_jur_form']:
            title_ids = self.env['res.partner.title'].search(
                [('domain', '=', 'partner'), ('name', '=', record['cweb_jur_form'])])
            if not title_ids:
                title_id = self.env['res.partner.title'].create({
                    'domain': 'partner',
                    'name': record['cweb_jur_form'],
                    })
            else:
                title_id = title_ids[0]
            res['title'] = title_id.id
        return res

    @api.one
    def button_cweb_apply(self):
        self.write(self._companyweb_values_to_update(self.read(load='_classic_write')[0]))
