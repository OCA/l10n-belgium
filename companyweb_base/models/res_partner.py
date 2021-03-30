# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import html
import logging
from datetime import datetime
from hashlib import sha1

import zeep

from odoo import _, api, fields, models, modules
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Companyweb is ok with those key being visible on github
SERVICE_INTEGRATOR_ID = "acsone"
SERVICE_INTEGRATOR_SECRET = "ECAB8ACF-9AE1-4E90-BD0D-05A1F47A3FE9"


class CompanywebPartner(models.Model):
    _inherit = "res.partner"
    cweb_currency_id = fields.Many2one(
        "res.currency", string="Companyweb currency", readonly=True
    )
    cweb_lastupdate = fields.Datetime("Companyweb Last Update", readonly=True)
    cweb_name = fields.Char("Companyweb Name", readonly=True)
    cweb_name_enable = fields.Boolean("Companyweb Name Enabled", readonly=True)
    cweb_jur_form = fields.Char("Companyweb Juridical Form", readonly=True)
    cweb_jur_form_enable = fields.Boolean(
        "Companyweb Juridical Form Enabled", readonly=True
    )
    cweb_companystatus = fields.Char("Companyweb Company Status", readonly=True)
    cweb_companystatus_code = fields.Char(
        "Companyweb Company StatusCode", readonly=True
    )
    cweb_companystatus_enable = fields.Boolean(
        "Companyweb Company Status Enabled", readonly=True
    )
    cweb_street = fields.Char("Companyweb Street", readonly=True)
    cweb_zip = fields.Char("Companyweb Postal code", readonly=True)
    cweb_city = fields.Char("Companyweb City", readonly=True)
    cweb_country = fields.Many2one(
        "res.country", string="Companyweb Country", readonly=True
    )
    cweb_address_enable = fields.Boolean("Companyweb Address Enabled", readonly=True)

    cweb_creditLimit = fields.Float("Companyweb Credit limit", readonly=True)
    cweb_creditLimit_unset = fields.Boolean(
        "Companyweb Credit limit Unset", readonly=True
    )
    cweb_creditLimit_enable = fields.Boolean(
        "Companyweb Credit limit Enabled", readonly=True
    )
    cweb_creditLimit_info = fields.Char("Companyweb Credit limit Info", readonly=True)
    cweb_creditLimit_info_unset = fields.Boolean(
        "Companyweb Credit limit Info Unset", readonly=True
    )

    cweb_startDate = fields.Date("Companyweb Start Date", readonly=True)
    cweb_startDate_enable = fields.Boolean(
        "Companyweb Start Date Enabled", readonly=True
    )
    cweb_endDate = fields.Date("Companyweb End Date", readonly=True)
    cweb_endDate_enable = fields.Boolean("Companyweb End date Enabled", readonly=True)
    cweb_score = fields.Char("Companyweb Score", readonly=True)
    cweb_score_enable = fields.Boolean("Companyweb Score Enabled", readonly=True)

    cweb_image_tag = fields.Html(
        "Companyweb Barometer Image tag", compute="_compute_cweb_image", readonly=True
    )
    cweb_image = fields.Char("Companyweb Barometer Image", readonly=True)
    cweb_image_unset = fields.Boolean("Companyweb Barometer Image Unset", readonly=True)

    cweb_warnings = fields.Html("Companyweb Warnings", readonly=True)
    cweb_warnings_enable = fields.Boolean("Companyweb Warnings Enabled", readonly=True)
    cweb_url = fields.Char("Companyweb Detailed Report", readonly=True)
    cweb_url_enable = fields.Boolean(
        "Companyweb Detailed Report Enabled", readonly=True
    )
    cweb_url_report = fields.Char("Companyweb Url Report", readonly=True)
    cweb_url_report_enable = fields.Boolean(
        "Companyweb Url Report Enabled", readonly=True
    )
    cweb_vat_liable = fields.Boolean("Companyweb Subject to VAT", readonly=True)
    cweb_vat_liable_enable = fields.Boolean(
        "Companyweb Subject to VAT Enabled", readonly=True
    )
    cweb_balance_data_enable = fields.Boolean(
        "Companyweb Balance Data Enabled", readonly=True
    )
    cweb_balance_year = fields.Char("Companyweb Balance Year", readonly=True)
    cweb_balance_year_unset = fields.Boolean(
        "Companyweb Balance Year Unset", readonly=True
    )
    cweb_closed_date = fields.Date("Companyweb Closed Date", readonly=True)
    cweb_closed_date_unset = fields.Boolean(
        "Companyweb Closed Date Unset", readonly=True
    )
    cweb_equityCapital = fields.Float("Companyweb Equity Capital", readonly=True)
    cweb_equityCapital_unset = fields.Boolean(
        "Companyweb Equity Capital Unset", readonly=True
    )
    cweb_average_fte = fields.Float(
        "Companyweb Average number of staff in FTE", readonly=True
    )
    cweb_average_fte_unset = fields.Boolean(
        "Companyweb Average number of staff in FTE Unset", readonly=True
    )
    cweb_addedValue = fields.Float("Companyweb Gross Margin (+/-)", readonly=True)
    cweb_addedValue_unset = fields.Boolean(
        "Companyweb Gross Margin (+/-) Unset", readonly=True
    )
    cweb_turnover = fields.Float("Companyweb Turnover", readonly=True)
    cweb_turnover_unset = fields.Boolean("Companyweb Turnover Unset", readonly=True)
    cweb_result = fields.Float(
        "Companyweb Fiscal Year Profit/Loss (+/-)", readonly=True
    )
    cweb_result_unset = fields.Boolean(
        "Companyweb Fiscal Year Profit/Loss (+/-) Unset", readonly=True
    )
    cweb_prefLang = fields.Many2one(
        "res.lang", string="Companyweb Preferred Language", readonly=True
    )
    cweb_prefLang_enable = fields.Boolean(
        "Companyweb Preferred Language Enabled", readonly=True
    )

    cweb_show_button_enhance = fields.Boolean(
        "Companyweb Button Enhance Enabled", compute="_compute_cweb_show_button_enhance"
    )
    cweb_show_button_address = fields.Boolean(
        "Companyweb Button Address Enabled", compute="_compute_cweb_show_button_address"
    )
    cweb_show_tab = fields.Boolean(
        "Companyweb Tab Enabled", compute="_compute_cweb_cweb_show_tab"
    )

    @api.depends("cweb_image")
    def _compute_cweb_image(self):
        for rec in self:
            if rec.cweb_image:
                img_url = modules.module.get_resource_path(
                    "companyweb_base", "static", "img", "cweb_barometer", rec.cweb_image
                )
                if img_url:
                    img_url = (
                        "/companyweb_base/static/img/cweb_barometer/%s" % rec.cweb_image
                    )
                    rec.cweb_image_tag = '<img src="%s"/>' % img_url
                else:
                    rec.cweb_image_tag = None
            else:
                rec.cweb_image_tag = None

    @api.depends("is_company", "vat")
    def _compute_cweb_show_button_enhance(self):
        """for the button t be show
        the partner has to be a company and the partner.vat should be BE000000000"""
        for rec in self:
            if rec.is_company and rec.vat and rec.vat.startswith("BE"):
                rec.cweb_show_button_enhance = True
            else:
                rec.cweb_show_button_enhance = False

    @api.depends(
        "cweb_address_enable",
        "cweb_street",
        "cweb_zip",
        "cweb_city",
        "cweb_country",
    )
    def _compute_cweb_show_button_address(self):
        """for the button to be show
        the partner has have cweb_address enabled and data for the address field"""
        for rec in self:
            if (
                rec.cweb_address_enable
                and rec.cweb_street
                and rec.cweb_zip
                and rec.cweb_city
                and rec.cweb_country
            ):
                rec.cweb_show_button_address = True
            else:
                rec.cweb_show_button_address = False

    @api.depends(
        "cweb_name_enable",
        "cweb_jur_form_enable",
        "cweb_address_enable",
        "cweb_creditLimit_enable",
        "cweb_startDate_enable",
        "cweb_endDate_enable",
        "cweb_score_enable",
        "cweb_warnings_enable",
        "cweb_url_enable",
        "cweb_vat_liable_enable",
        "cweb_balance_data_enable",
        "cweb_prefLang_enable",
        "cweb_companystatus_enable",
        "cweb_url_report_enable",
    )
    def _compute_cweb_cweb_show_tab(self):
        """for the tab with data to be shown
        at least one of the field _enable has to be true"""
        for rec in self:
            if (
                rec.cweb_name_enable
                or rec.cweb_jur_form_enable
                or rec.cweb_address_enable
                or rec.cweb_creditLimit_enable
                or rec.cweb_startDate_enable
                or rec.cweb_endDate_enable
                or rec.cweb_score_enable
                or rec.cweb_warnings_enable
                or rec.cweb_url_enable
                or rec.cweb_vat_liable_enable
                or rec.cweb_balance_data_enable
                or rec.cweb_prefLang_enable
                or rec.cweb_companystatus_enable
                or rec.cweb_url_report_enable
            ):
                rec.cweb_show_tab = True
            else:
                rec.cweb_show_tab = False

    def _cweb_create_hash(self, login, password, secret):
        """method used for the API call
        it generates the 'loginhash' needed by the API"""
        today = datetime.now().strftime("%Y%m%d")
        text = (today + login + password + secret).lower()
        return sha1(text.encode("utf-8")).hexdigest()

    def _cweb_get_country(self, country_code):
        country = self.env["res.country"].search([("code", "=", country_code.upper())])
        return country

    def _cweb_populate_general(self, cweb_response):
        self.cweb_lastupdate = datetime.now()
        self.cweb_name_enable = cweb_response["CompanyName"]["IsEnabled"]
        cweb_has_name_value = cweb_response["CompanyName"]["Value"]
        if self.cweb_name_enable and cweb_has_name_value:
            self.cweb_name = cweb_has_name_value
        else:
            self.cweb_name = None

        self.cweb_jur_form_enable = cweb_response["LegalForm"]["IsEnabled"]
        cweb_has_jur_form_value = cweb_response["LegalForm"]["Value"]
        if self.cweb_jur_form_enable and cweb_has_jur_form_value:
            self.cweb_jur_form = cweb_has_jur_form_value["Abbreviation"]
        else:
            self.cweb_jur_form = None

        self.cweb_prefLang_enable = cweb_response["PreferredLanguages"]["IsEnabled"]
        cweb_has_prefLang_value = cweb_response["PreferredLanguages"]["Value"]
        if self.cweb_prefLang_enable and cweb_has_prefLang_value:
            cweb_lang = cweb_response["PreferredLanguages"]["Value"]["LanguageString"]
            lang = (
                self.env["res.lang"]
                .with_context(active_test=False)
                .search([("iso_code", "=", cweb_lang)])
            )
            self.cweb_prefLang = lang
        else:
            self.cweb_prefLang = None

        self.cweb_companystatus_enable = cweb_response["CompanyStatus"]["IsEnabled"]
        cweb_has_companystatus_value = cweb_response["CompanyStatus"]["Value"]
        if self.cweb_companystatus_enable and cweb_has_companystatus_value:
            self.cweb_companystatus = cweb_has_companystatus_value["Info"]
            self.cweb_companystatus_code = cweb_has_companystatus_value["Code"]
        else:
            self.cweb_companystatus = None
            self.cweb_companystatus_code = None

        self.cweb_vat_liable_enable = cweb_response["VatEnabled"]["IsEnabled"]
        cweb_has_vat_liable_value = cweb_response["VatEnabled"]["Value"]
        if self.cweb_vat_liable_enable and cweb_has_vat_liable_value:
            self.cweb_vat_liable = cweb_has_vat_liable_value
        else:
            self.cweb_vat_liable = None

    def _cweb_populate_address(self, cweb_response):
        self.cweb_address_enable = cweb_response["Address"]["IsEnabled"]
        cweb_has_address_value = cweb_response["Address"]["Value"]
        if self.cweb_address_enable and cweb_has_address_value:
            self.cweb_street = cweb_has_address_value["Line1"]
            self.cweb_zip = cweb_has_address_value["PostalCode"]
            self.cweb_city = cweb_has_address_value["City"]
            self.cweb_country = self._cweb_get_country(
                cweb_has_address_value["CountryCode"]
            )
        else:
            self.cweb_street = None
            self.cweb_zip = None
            self.cweb_city = None
            self.cweb_country = None

    def _cweb_populate_balans(self, cweb_response):
        self.cweb_balance_data_enable = cweb_response["Balances"]["IsEnabled"]
        cweb_has_balance_value = cweb_response["Balances"]["Value"]
        if self.cweb_balance_data_enable and cweb_has_balance_value:
            currency = self.env["res.currency"].search([("name", "=", "EUR")])
            self.cweb_currency_id = currency
            self.cweb_balance_year = cweb_has_balance_value["Balans"][0]["BookYear"]
            self.cweb_balance_year_unset = True
            balans_data = cweb_has_balance_value["Balans"][0]["BalansData"][
                "BalansData"
            ]
            for data in balans_data:
                if data["Key"] == "CloseDate":
                    try:
                        self.cweb_closed_date = datetime.strptime(
                            str(data["Value"]), "%Y-%m-%d"
                        )
                    except ValueError:
                        self.cweb_closed_date = None
                        self.cweb_closed_date_unset = False
                if data["Key"] == "Rub10_15":
                    value = data["Value"]
                    self._cweb_set_equityCapital_data(value)
                if data["Key"] == "Rub70":
                    value = data["Value"]
                    self._cweb_set_turnover_date(value)
                if data["Key"] == "Rub9087":
                    value = data["Value"]
                    self._cweb_set_average_fte_data(value)
                if data["Key"] == "Rub9800":
                    value = data["Value"]
                    self._cweb_set_addedValue_data(value)
                if data["Key"] == "Rub9904":
                    value = data["Value"]
                    self._cweb_set_result_data(value)

        elif self.cweb_balance_data_enable and not cweb_has_balance_value:
            self._cweb_unset_balans_date()
            self._cweb_empty_balans_data()
        else:
            self._cweb_empty_balans_data()

    def _cweb_set_equityCapital_data(self, value):
        if value or value == 0:
            self.cweb_equityCapital = float(value)
            self.cweb_equityCapital_unset = True
        else:
            self.cweb_equityCapital_unset = False

    def _cweb_set_turnover_date(self, value):
        if value or value == 0:
            self.cweb_turnover_unset = True
            self.cweb_turnover = float(value)
        else:
            self.cweb_turnover_unset = False

    def _cweb_set_average_fte_data(self, value):
        if value or value == 0:
            self.cweb_average_fte_unset = True
            self.cweb_average_fte = float(value)
        else:
            self.cweb_average_fte_unset = False

    def _cweb_set_addedValue_data(self, value):
        if value or value == 0:
            self.cweb_addedValue = float(value)
            self.cweb_addedValue_unset = True
        else:
            self.cweb_addedValue_unset = False

    def _cweb_set_result_data(self, value):
        if value or value == 0:
            self.cweb_result = float(value)
            self.cweb_result_unset = True
        else:
            self.cweb_result_unset = False

    def _cweb_unset_balans_date(self):
        self.cweb_closed_date_unset = False
        self.cweb_equityCapital_unset = False
        self.cweb_turnover_unset = False
        self.cweb_average_fte_unset = False
        self.cweb_addedValue_unset = False
        self.cweb_result_unset = False

    def _cweb_empty_balans_data(self):
        self.cweb_closed_date = False
        self.cweb_equityCapital = False
        self.cweb_turnover = False
        self.cweb_average_fte = False
        self.cweb_addedValue = False
        self.cweb_result = False
        self.cweb_balance_year = False

    def _cweb_populate_url(self, cweb_response):
        self.cweb_url_enable = cweb_response["DetailUrl"]["IsEnabled"]
        cweb_has_url_value = cweb_response["DetailUrl"]["Value"]
        if self.cweb_url_enable and cweb_has_url_value:
            self.cweb_url = cweb_has_url_value
        else:
            self.cweb_url = None
        self.cweb_url_report_enable = cweb_response["ReportUrl"]["IsEnabled"]

        cweb_has_url_report_value = cweb_response["ReportUrl"]["Value"]
        if self.cweb_url_report_enable and cweb_has_url_report_value:
            self.cweb_url_report = cweb_has_url_report_value
        else:
            self.cweb_url_report = None

    def _cweb_populate_dates(self, cweb_response):
        self.cweb_startDate_enable = cweb_response["StartDate"]["IsEnabled"]
        cweb_has_startDate_value = cweb_response["StartDate"]["Value"]
        if self.cweb_startDate_enable and cweb_has_startDate_value:
            try:
                self.cweb_startDate = datetime.strptime(
                    str(cweb_response["StartDate"]["Value"]), "%Y%m%d"
                )
            except ValueError:
                self.cweb_startDate = None
        else:
            self.cweb_startDate = None

        self.cweb_endDate_enable = cweb_response["EndDate"]["IsEnabled"]
        cweb_has_endDate_value = cweb_response["EndDate"]["Value"]
        if self.cweb_endDate_enable and cweb_has_endDate_value:
            try:
                self.cweb_endDate = datetime.strptime(
                    str(cweb_response["EndDate"]["Value"]), "%Y%m%d"
                )
            except ValueError:
                self.cweb_endDate = False
        else:
            self.cweb_endDate = None

    def _cweb_populate_score(self, cweb_response):
        self.cweb_score_enable = cweb_response["Score"]["IsEnabled"]
        cweb_has_score_value = cweb_response["Score"]["Value"]
        if self.cweb_score_enable and cweb_has_score_value:
            self.cweb_score = cweb_response["Score"]["Value"]["ScoreAsInt"]
            cweb_has_cweb_image_value = cweb_response["Score"]["Value"]["ScoreImage"]
            if cweb_has_cweb_image_value:
                self.cweb_image_unset = True
                self.cweb_image = cweb_response["Score"]["Value"]["ScoreImage"]
            else:
                self.cweb_image_unset = False
        else:
            self.cweb_score = None
            self.cweb_image = None
            self.cweb_image_unset = False

    def _cweb_populate_data(self, cweb_response):

        self.cweb_creditLimit_enable = cweb_response["CreditLimit"]["IsEnabled"]
        cweb_has_creditLimit_value = cweb_response["CreditLimit"]["Value"]
        if self.cweb_creditLimit_enable and cweb_has_creditLimit_value:
            limit = cweb_response["CreditLimit"]["Value"]["Limit"]
            if limit or limit == 0:
                self.cweb_creditLimit = limit
                self.cweb_creditLimit_unset = True
            else:
                self.cweb_creditLimit_unset = False
                self.cweb_creditLimit = None
            if cweb_response["CreditLimit"]["Value"]["Info"]:
                self.cweb_creditLimit_info = cweb_response["CreditLimit"]["Value"][
                    "Info"
                ]
                self.cweb_creditLimit_info_unset = True
                self.cweb_creditLimit_info = None
            else:
                self.cweb_creditLimit_info_unset = False
        else:
            self.cweb_creditLimit = None
            self.cweb_creditLimit_info = None
            self.cweb_creditLimit_info_unset = False
            self.cweb_creditLimit_unset = False

        self.cweb_warnings_enable = cweb_response["WarningsOverview"]["IsEnabled"]
        cweb_has_warnings_value = cweb_response["WarningsOverview"]["Value"]
        if self.cweb_warnings_enable and cweb_has_warnings_value:
            if cweb_has_warnings_value["Warnings"]:
                self.cweb_warnings = ""
                for rec in cweb_has_warnings_value["Warnings"]["string"]:
                    self.cweb_warnings += "- " + html.escape(rec) + "<br/>"
            else:
                self.cweb_warnings = None
        elif self.cweb_warnings_enable:
            self.cweb_warnings = None
        else:
            self.cweb_warnings = None

    def cweb_button_enhance(self):
        """Main logic of the module
        Validate that the logged in user has credentials
        make the API CALL
        based on status make decision
        When status is ok -> populate fields"""
        if not self.env.user.has_group("companyweb_base.cweb_download"):
            raise UserError(_("Companyweb : You don't have access"))
        user_login = self.env.user.cweb_login
        user_password = self.env.user.cweb_password
        user_lang = self.env.context.get("lang")[:2].upper()
        if user_lang not in ["FR", "NL"]:
            user_lang = "EN"

        if not user_login or not user_password:
            return self._cweb_call_wizard_credentials("Enter Companyweb credentials")

        client = zeep.Client("https://connect.companyweb.be/V1.3/alacarteservice.asmx")
        r = client.service.GetCompanyByVat(
            dict(
                CompanyWebLogin=user_login,
                CompanyWebPassword=user_password,
                ServiceIntegrator=SERVICE_INTEGRATOR_ID,
                LoginHash=self._cweb_create_hash(
                    user_login, user_password, SERVICE_INTEGRATOR_SECRET
                ),
                Language=user_lang,
                VatNumber=self.vat,
            )
        )
        if r["StatusCode"] in [101, 302]:
            return self._cweb_call_wizard_credentials("Enter Companyweb credentials")
        elif r["StatusCode"] != 0:
            raise UserError(
                _("Companyweb status : %s : %s ", r["StatusCode"], r["StatusMessage"])
            )

        cweb_response = r["CompanyResponse"]
        self._cweb_populate_general(cweb_response)
        self._cweb_populate_address(cweb_response)
        self._cweb_populate_balans(cweb_response)
        self._cweb_populate_url(cweb_response)
        self._cweb_populate_dates(cweb_response)
        self._cweb_populate_score(cweb_response)
        self._cweb_populate_data(cweb_response)
        self.env.user.notify_success(message=_("Companyweb Enhance OK"))

    def cweb_button_copy_address(self):

        if not self.env.user.has_group("companyweb_base.cweb_view"):
            raise UserError(_("Companyweb : You don't have access"))
        self.street = self.cweb_street
        self.city = self.cweb_city
        self.zip = self.cweb_zip
        self.country_id = self.cweb_country
        self.street2 = None
        self.state_id = None
        self.env.user.notify_success(
            message=_("Companyweb Address Successfully copied")
        )

    def _cweb_call_wizard_credentials(self, wizard_name):
        wizard_form = self.env.ref("companyweb_base.companyweb_credential_wizard")
        return {
            "name": wizard_name,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "companyweb_base.credential_wizard",
            "view_id": wizard_form.id,
            "target": "new",
            "context": self.env.context,
        }
