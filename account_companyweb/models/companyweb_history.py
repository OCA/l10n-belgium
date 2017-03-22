# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Author: Adrien Peiffer
#    Contributor: Jacques-Etienne Baudoux <je@bcim.be> BCIM sprl
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    Copyright (c) 2015 BCIM sprl (http://www.bcim.be)
#    Copyright (c) 2017 Okia SPRL (https://okia.be)
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
from datetime import datetime
import logging

from openerp import fields, models, api

from . import companyweb_rest

_logger = logging.getLogger(__name__)


class CompanywebHistory(models.Model):
    _name = 'companyweb.history'
    _order = 'date DESC'
    _rec_name = 'date'

    date = fields.Date(required=True)
    info = fields.Text()
    state = fields.Selection([('success', 'Success'),
                              ('error', 'Error')], default='success')
    nbr_of_customers = fields.Integer(string='Number of customers',
                                      compute='_compute_nbr_of_customers',
                                      readonly=True)
    line_ids = fields.One2many('companyweb.history.line',
                               'history_id',
                               string='Lines',
                               readonly=True)

    @api.multi
    def _compute_nbr_of_customers(self):
        for history in self:
            history.nbr_of_customers = len(history.line_ids)

    @api.model
    def fetch_new_modification(self):
        login = self.env['ir.config_parameter'].get_param('companyweb.login')
        pswd = self.env['ir.config_parameter'].get_param('companyweb.pswd')

        params = {
            'login': login,
            'pswd': pswd,
        }

        result = companyweb_rest.companyweb_get_summary(**params)
        summary = [(value['date'], value['nbr']) for value in result]

        summary = sorted(summary, key=lambda x: x[0])

        for date_to_retrieve, nbr in summary:
            modification_date = datetime.strptime(date_to_retrieve, '%Y%m%d')
            nbr_of_customers = int(nbr)

            date_str = fields.Date.to_string(modification_date)
            existing_history = self.search([('date', '=', date_str),
                                            ('state', '=', 'success')])
            if existing_history:
                continue

            history = self.create({
                'date': fields.Date.to_string(modification_date),
                'nbr_of_customers': nbr_of_customers
            })

            try:
                history.retrieve_partners()
            except Exception as e:
                history.info = str(e)
                _logger.error(str(e))

    @api.multi
    def retrieve_partners(self):
        self.ensure_one()

        login = self.env['ir.config_parameter'].get_param('companyweb.login')
        pswd = self.env['ir.config_parameter'].get_param('companyweb.pswd')

        modification_date = fields.Date.from_string(self.date)
        formatted_day = modification_date.strftime('%Y%m%d')

        params = {
            'login': login,
            'pswd': pswd,
            'day': formatted_day,
        }
        vats = companyweb_rest.companyweb_get_allchange(**params)

        missing_partners = []
        duplicate_partners = []
        for vat in vats:
            partner = self.env['res.partner'].search([('vat', 'ilike', 'BE' + vat)])
            if not partner:
                missing_partners.append(vat)
                continue
            elif len(partner) > 1:
                duplicate_partners.append(vat)
                continue

            params = {
                'login': login,
                'pswd': pswd,
                'day': formatted_day,
                'vat': vat,
            }
            data = companyweb_rest.companyweb_get_last_change(**params)
            values = {'cweb_lastupdate': fields.Datetime.now()}
            for k, v in data.iteritems():
                key = "cweb_%s" % k
                if key in self.env['res.partner']._all_columns:
                    values[key] = v

            partner.write(values)

            self.env['companyweb.history.line'].create({
                'history_id': self.id,
                'partner_id': partner.id,
                'data': data,
            })

        info = ''
        if missing_partners:
            info += '\nSome customers were not found:\n{}'\
                .format('\n'.join(missing_partners))

        if duplicate_partners:
            info += '\nSome customers have the same vat number:\n{}' \
                .format('\n'.join(missing_partners))

        if info:
            self.info = info


class CompanywebHistoryLine(models.Model):
    _name = 'companyweb.history.line'

    history_id = fields.Many2one('companyweb.history',
                                 string='History',
                                 required=True)
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 required=True)
    partner_vat = fields.Char('VAT',
                              related='partner_id.vat',
                              readonly=True)
    data = fields.Text('Data')
