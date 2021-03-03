# -*- coding: utf-8 -*-
# Copyright 2021-2023 ACSONE SA/NV
from odoo import api, fields, models
from datetime import datetime
from hashlib import sha1
import zeep
from odoo.exceptions import ValidationError


class CompanyWebPartner(models.Model):
    _inherit = 'res.partner'
    cweb_lastupdate = fields.Datetime('Company Web Last Update', readonly=True)
    cweb_name = fields.Char('CompanyWeb Name', readonly=True)
    cweb_name_enable = fields.Boolean()
    cweb_jur_form = fields.Char('CompanyWeb Juridical Form', readonly=True)
    cweb_jur_form_enable = fields.Boolean()
    cweb_street = fields.Char('CompanyWeb Street', readonly=True)
    cweb_zip = fields.Char('CompanyWeb Postal code', readonly=True)
    cweb_city = fields.Char('CompanyWeb City', readonly=True)
    cweb_country = fields.Char('CompanyWeb Country', readonly=True)
    cweb_address_enable = fields.Boolean()
    cweb_creditLimit = fields.Float('CompanyWeb Credit limit', readonly=True)
    cweb_creditLimit_enable = fields.Boolean()
    cweb_startDate = fields.Date('CompanyWeb Start date', readonly=True)
    cweb_startDate_enable = fields.Boolean()
    cweb_endDate = fields.Date('CompanyWeb End date', readonly=True)
    cweb_endDate_enable = fields.Boolean()
    cweb_score = fields.Char('CompanyWeb Score', readonly=True)
    cweb_score_enable = fields.Boolean()
    cweb_image = fields.Char(readonly=True)
    cweb_warnings = fields.Text('CompanyWeb Warnings', readonly=True)
    cweb_warnings_enable = fields.Boolean()
    cweb_url = fields.Char('CompanyWeb Detailed Report', readonly=True)
    cweb_url_enable = fields.Boolean()
    cweb_vat_liable = fields.Boolean("CompanyWeb Subject to VAT", readonly=True)
    cweb_vat_liable_enable = fields.Boolean()
    cweb_balance_year = fields.Char("CompanyWeb Balance Year", readonly=True)
    cweb_balance_year_enable = fields.Boolean()
    cweb_equityCapital = fields.Float('CompanyWeb Equity Capital', readonly=True)
    cweb_addedValue = fields.Float('CompanyWeb Gross Margin (+/-)', readonly=True)
    cweb_turnover = fields.Float('CompanyWeb Turnover', readonly=True)
    cweb_result = fields.Float('CompanyWeb Fiscal Year Profit/Loss (+/-)', readonly=True)
    cweb_prefLang = fields.Char('CompanyWeb Preferred Language', readonly=True)
    cweb_prefLang_enable = fields.Boolean()

    def create_hash(self, login, password, secret):
        today = datetime.now().strftime("%Y%m%d")
        text = (today + login + password + secret).lower()
        return sha1(text.encode('utf-8')).hexdigest()

    def button_companyweb(self):
        SERVICE_INTEGRATOR_ID = "acsone"
        SERVICE_INTEGRATOR_SECRET = "ECAB8ACF-9AE1-4E90-BD0D-05A1F47A3FE9"
        LOGIN = self.env.user.cweb_login
        PASSWORD = self.env.user.cweb_password
        if not LOGIN or not PASSWORD:
            wizard_form = self.env.ref('companyweb_base.companyweb_user_wizard', False)
            return {
                'name': "No Credentials",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'companyweb_base.user_wizard',
                'view_id': wizard_form.id,
                'target': 'new'
            }

        client = zeep.Client("https://connect.companyweb.be/V1.3/alacarteservice.asmx")
        r = client.service.GetCompanyByVat(dict(
            CompanyWebLogin=LOGIN,
            CompanyWebPassword=PASSWORD,
            ServiceIntegrator=SERVICE_INTEGRATOR_ID,
            LoginHash=self.create_hash(LOGIN, PASSWORD, SERVICE_INTEGRATOR_SECRET),
            Language="FR",
            VatNumber=self.vat,
        ))
        print(r['StatusCode'])
        if r['StatusCode'] == 101:
            wizard_form = self.env.ref('companyweb_base.companyweb_user_wizard', False)
            return {
                'name': "Bad Credentials",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'companyweb_base.user_wizard',
                'view_id': wizard_form.id,
                'target': 'new'
            }
        elif r['StatusCode'] == 306:
            raise ValidationError((self.vat + ' is not a valid belgian vatnumber or empty.'))

        self.cweb_lastupdate = datetime.now()
        self.cweb_name_enable = r['CompanyResponse']['CompanyName']['IsEnabled']
        if self.cweb_name_enable:
            self.cweb_name = r['CompanyResponse']['CompanyName']['Value']
        self.cweb_jur_form_enable = r['CompanyResponse']['LegalForm']['IsEnabled']
        if self.cweb_jur_form_enable:
            self.cweb_jur_form = r['CompanyResponse']['LegalForm']['Value']['Abbreviation']
        self.cweb_address_enable = r['CompanyResponse']['Address']['IsEnabled']
        if self.cweb_address_enable:
            self.cweb_street = r['CompanyResponse']['Address']['Value']['Line1']
            self.cweb_zip = r['CompanyResponse']['Address']['Value']['PostalCode']
            self.cweb_city = r['CompanyResponse']['Address']['Value']['City']
            self.cweb_country = r['CompanyResponse']['Address']['Value']['CountryCode']

        self.cweb_creditLimit_enable = r['CompanyResponse']['CreditLimit']['IsEnabled']
        if self.cweb_creditLimit_enable:
            self.cweb_creditLimit = r['CompanyResponse']['CreditLimit']['Value']['Limit']

        self.cweb_startDate_enable = r['CompanyResponse']['StartDate']['IsEnabled']
        if self.cweb_startDate_enable:
            try:
                self.cweb_startDate = datetime.strptime(str(r['CompanyResponse']['StartDate']['Value']), '%Y%m%d')
            except ValueError:
                self.cweb_startDate = None
        self.cweb_endDate_enable = r['CompanyResponse']['EndDate']['IsEnabled']
        if self.cweb_endDate_enable:
            try:
                self.cweb_endDate = datetime.strptime(str(r['CompanyResponse']['EndDate']['Value']), '%Y%m%d')
            except ValueError:
                self.cweb_endDate = None
        self.cweb_score_enable = r['CompanyResponse']['Score']['IsEnabled']
        if self.cweb_score_enable:
            self.cweb_score = r['CompanyResponse']['Score']['Value']['ScoreAsInt']
            self.cweb_image = r['CompanyResponse']['Score']['Value']['ScoreImage']
        self.cweb_warnings_enable = r['CompanyResponse']['WarningsOverview']['IsEnabled']
        if self.cweb_warnings_enable:
            self.cweb_warnings = r['CompanyResponse']['WarningsOverview']['Value']['Warnings']['string']
        self.cweb_url_enable = r['CompanyResponse']['DetailUrl']['IsEnabled']
        if self.cweb_url_enable:
            self.cweb_url = r['CompanyResponse']['DetailUrl']['Value']
        self.cweb_vat_liable_enable = r['CompanyResponse']['VatEnabled']['IsEnabled']
        if self.cweb_vat_liable_enable:
            self.cweb_vat_liable = r['CompanyResponse']['VatEnabled']['Value']
        self.cweb_balance_year_enable = r['CompanyResponse']['Balances']['IsEnabled']
        if self.cweb_balance_year_enable:
            self.cweb_balance_year = r['CompanyResponse']['Balances']['Value']['Balans'][0]['BookYear']
            balans_data = r['CompanyResponse']['Balances']['Value']['Balans'][0]['BalansData']['BalansData']
            self.cweb_equityCapital = balans_data[1]['Value']
            self.cweb_addedValue = balans_data[4]['Value']
            self.cweb_turnover = balans_data[2]['Value']
            self.cweb_result = balans_data[5]['Value']
        self.cweb_prefLang_enable = r['CompanyResponse']['PreferredLanguages']['IsEnabled']
        if self.cweb_prefLang_enable:
            self.cweb_prefLang = r['CompanyResponse']['PreferredLanguages']['Value']['LanguageString']
