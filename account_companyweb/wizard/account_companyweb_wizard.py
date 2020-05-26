# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Author: Adrien Peiffer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

SUPERUSER_ID = 1


class account_companyweb_wizard(models.TransientModel):

    _name = 'account.companyweb.wizard'

    vat_number = fields.Text('VAT number', readonly=True)
    name = fields.Text('Name', readonly=True)
    jur_form = fields.Text('Juridical Form', readonly=True)
    street = fields.Text('Address', readonly=True)
    zip = fields.Text('Postal code', readonly=True)
    city = fields.Text('City', readonly=True)
    creditLimit = fields.Float('Credit limit', readonly=True)
    startDate = fields.Date('Start Date', readonly=True)
    endDate = fields.Date('End Date', readonly=True)
    image = fields.Binary('Health barometer', readonly=True)
    warnings = fields.Text('Warnings', readonly=True)
    url = fields.Char('Detailed Report', readonly=True)
    vat_liable = fields.Boolean("Subject to VAT", readonly=True)
    balance_year = fields.Text("Balance year", readonly=True)
    equityCapital = fields.Float('Equity Capital', readonly=True)
    addedValue = fields.Float('Gross Margin (+/-)', readonly=True)
    turnover = fields.Float('Turnover', readonly=True)
    result = fields.Float('Fiscal Year Profit/Loss (+/-)', readonly=True)

    def get_update_values(self,  wizard):
        """ This method is designed to be inherited to add some field to
            update on res.partner"""
        return {'name': wizard.name,
                'is_company': True,
                'street': wizard.street,
                'city': wizard.city,
                'zip': wizard.zip,
                'credit_limit': wizard.creditLimit,
                }

    def update_information(self):
        context = self.env.context
        res_partner_model = self.env['res.partner']
        partner_id = context['active_id']
        this = self.browse(self.ids)[0]
        update_values = self.get_update_values(this)
        res = res_partner_model.browse(partner_id).write(update_values)
        return res
