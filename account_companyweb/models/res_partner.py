# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)

import logging

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

from . import companyweb_rest

logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # prefix fields by "CompanyWeb" to allow easy identification in export

    cweb_lastupdate = fields.Datetime('CompanyWeb Last update', readonly=True)

    cweb_name = fields.Char('CompanyWeb Name', readonly=True)
    cweb_jur_form = fields.Char('CompanyWeb Juridical Form', readonly=True)
    cweb_street = fields.Char('CompanyWeb Street', readonly=True)
    cweb_zip = fields.Char('CompanyWeb Postal code', readonly=True)
    cweb_city = fields.Char('CompanyWeb City', readonly=True)
    cweb_creditLimit = fields.Float('CompanyWeb Credit limit', readonly=True)
    cweb_startDate = fields.Date('CompanyWeb Start date', readonly=True)
    cweb_endDate = fields.Date('CompanyWeb End date', readonly=True)
    cweb_score = fields.Char('CompanyWeb Score', readonly=True)
    cweb_image = fields.Binary('CompanyWeb Health barometer', readonly=True)
    cweb_warnings = fields.Text('CompanyWeb Warnings', readonly=True)
    cweb_url = fields.Char('CompanyWeb Detailed Report', readonly=True)
    cweb_vat_liable = fields.Boolean("CompanyWeb Subject to VAT",
                                     readonly=True)
    cweb_balance_year = fields.Char("CompanyWeb Balance Year",
                                    readonly=True)
    cweb_equityCapital = fields.Float('CompanyWeb Equity Capital',
                                      readonly=True)
    cweb_addedValue = fields.Float('CompanyWeb Gross Margin (+/-)',
                                   readonly=True)
    cweb_turnover = fields.Float('CompanyWeb Turnover', readonly=True)
    cweb_result = fields.Float('CompanyWeb Fiscal Year Profit/Loss (+/-)',
                               readonly=True)
    cweb_employees = fields.Float('CompanyWeb Number of Employees',
                                  readonly=True)
    cweb_prefLang = fields.Char('CompanyWeb Preferred Language', readonly=True)
    cweb_follow_customer = fields.Boolean('CompanyWeb follow customer',
                                          readonly=True)

    def _companyweb_information(self, vat_number):
        login = self.env['ir.config_parameter'].get_param('companyweb.login')
        pswd = self.env['ir.config_parameter'].get_param('companyweb.pswd')

        params = {
            'login': login,
            'pswd': pswd,
            'vat': vat_number,
            }

        if self._context.get('lang', '').startswith('fr'):
            params['lang'] = 1
        elif self._context.get('lang', '').startswith('nl'):
            params['lang'] = 2

        data = companyweb_rest.companyweb_getcompanydata(**params)

        values = {'cweb_lastupdate': fields.Datetime.now()}
        for k, v in data.iteritems():
            key = "cweb_%s" % k
            if key in self._all_columns:
                values[key] = v
        return values

    @api.one
    def button_cweb_fetch(self):
        self._cweb_refresh(force_update=True)

    @api.one
    def button_cweb_refresh(self):
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
                raise UserError(_("This company has no VAT number"))
            values = self._companyweb_information(vat_number)
            if force_update:
                values.update(self._companyweb_values_to_update(values))
            if not self.vat:
                values['vat'] = vat
            self.write(values)
            return

        raise UserError(_("Companyweb is only available for companies with a "
                        "Belgian VAT number"))

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
                [('domain', '=', 'partner'),
                 ('name', '=', record['cweb_jur_form'])])
            if not title_ids:
                title_id = self.env['res.partner.title'].create({
                    'domain': 'partner',
                    'name': record['cweb_jur_form'],
                    })
            else:
                title_id = title_ids[0]
            res['title'] = title_id.id

        if record['cweb_prefLang']:
            lang_ids = self.env['res.lang'].search(
                [('code', '=ilike', '%s%%' % record['cweb_prefLang'])])
            if lang_ids:
                res['lang'] = lang_ids[0].code

        return res

    @api.one
    def button_cweb_apply(self):
        self.write(self._companyweb_values_to_update(
            self.read(load='_classic_write')[0]))

    @api.multi
    def add_customer_to_companyvat(self):
        """
        Add new customers to Companyweb followers.
        :return:
        """
        login = self.env['ir.config_parameter'].get_param('companyweb.login')
        pswd = self.env['ir.config_parameter'].get_param('companyweb.pswd')

        for customer in self:
            if not customer.vat:
                continue

            params = {
                'login': login,
                'pswd': pswd,
                'vat': customer.vat,
            }

            companyweb_rest.companyweb_add_vat(**params)

        # Set the flag "CompanyWeb follow customer"
        self.write({'cweb_follow_customer': True})
