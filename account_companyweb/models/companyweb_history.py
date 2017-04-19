# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# Copyright (c) 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    nbr_of_errors = fields.Integer('Number of errors', readonly=True)
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
            partner = self.env['res.partner'].search(
                [('vat', 'ilike', 'BE0' + vat), ('is_company', '=', True)])
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

        info = []
        nbr_of_errors = 0
        if missing_partners:
            info += ['Some customers were not found:']
            info += missing_partners
            nbr_of_errors += len(missing_partners)

        if duplicate_partners:
            info += ['Some customers have the same vat number:']
            info += duplicate_partners
            nbr_of_errors += len(duplicate_partners)

        if info:
            self.info = '\n'.join(info)
            self.nbr_of_errors = nbr_of_errors


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
