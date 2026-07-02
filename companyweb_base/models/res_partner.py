# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from uuid import uuid4

from odoo import api, exceptions, fields, models, tools

from ..cweb_const import (
    ADDRESS_FIELDS,
    ALLOWED_COUNTRY_CODES,
    DATE_FIELDS,
    FILL_FIELD_MAP,
    FLOAT_FIELDS,
)
from ..cweb_format import (
    format_date,
    format_float_value,
    format_industry,
    format_liable_party,
    format_warnings,
    get_country_id,
    get_currency_id,
    get_lang_id,
)
from ..cweb_utils import (
    cweb_get,
    cweb_push,
    cweb_sync,
    get_all_enable_fields,
    get_balance_values,
    get_country_code_from_vat,
    get_data_values,
    get_nested_values,
)

CWEB_FIELD_ARGS = {"readonly": True, "copy": False}
CWEB_SYNC_STATUS_NONE = "none"
CWEB_SYNC_STATUS_PENDING = "pending"
CWEB_SYNC_STATUS_ACTIVE = "active"

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # System data
    cweb_lastupdate = fields.Datetime("Last Update", **CWEB_FIELD_ARGS)
    cweb_error = fields.Char(
        "Error", help="Error when enhancing contact with Companyweb"
    )

    # Cweb main data fields (in main response of API, comes with _enable field)
    cweb_name_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_name = fields.Char(
        "Companyweb Name",
        **CWEB_FIELD_ARGS,
        help="The official company name, for example 'Nationale Maatschappij Der "
        "Belgisch Spoorwegen' or 'Plopsa'.",
    )
    cweb_commercial_name_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_commercial_name = fields.Char(
        "Companyweb Commercial Name",
        **CWEB_FIELD_ARGS,
        help="Commercial company name, for example 'Plopsa Coo'",
    )
    cweb_jur_form_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_jur_form = fields.Char(
        "Legal Form",
        **CWEB_FIELD_ARGS,
        help="Legal form of the company, such as 'NV', 'SA', 'NP' etc.",
    )
    cweb_vat_liable_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_vat_liable = fields.Boolean(
        "Subject to VAT",
        **CWEB_FIELD_ARGS,
        help="Is the company subject to VAT or not",
    )
    cweb_vat_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_vat = fields.Char(
        "Companyweb VAT",
        **CWEB_FIELD_ARGS,
        help="Company VAT number",
    )
    cweb_prefLang_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_prefLang_id = fields.Many2one(
        "res.lang",
        string="Preferred Language",
        **CWEB_FIELD_ARGS,
        help="Preferred languages for communication, based on publication languages, "
        "among other factors.",
    )
    cweb_registry_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_registry = fields.Char(
        "Company Registry",
        **CWEB_FIELD_ARGS,
        help="The official registration number of a company. \n"
        "• Belgium: KBO, BCE, CBE\n"
        "• Netherlands: KvK\n"
        "• Luxembourg: RCS\n"
        "• France: SIREN",
    )
    cweb_country_code_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_country_code = fields.Char(
        "Companyweb Country Code",
        **CWEB_FIELD_ARGS,
        help="The official code of Belgium, The Netherlands, Luxembourg and France",
    )
    cweb_main_industry_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_main_industry = fields.Char(
        "Main Industry",
        **CWEB_FIELD_ARGS,
        help="The main activity of this company (NACE)",
    )
    cweb_industries_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_industries = fields.Text(
        "Other Activities",
        **CWEB_FIELD_ARGS,
        help="A list of the declared activities (NACE)",
    )
    cweb_email_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_email = fields.Char("Companyweb Email", **CWEB_FIELD_ARGS)
    cweb_website_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_website = fields.Char("Companyweb Website", **CWEB_FIELD_ARGS)
    cweb_phone_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_phone = fields.Char("Companyweb Phone", **CWEB_FIELD_ARGS)
    cweb_peppol_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_peppol = fields.Boolean(
        "Registered on Peppol",
        **CWEB_FIELD_ARGS,
        help="A PEPPOL ID is a unique identification code used within the PEPPOL "
        "network for electronic communication, enabling standardized invoicing, "
        "ordering, and reporting in compliance with EU regulations.",
    )
    cweb_sync_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_sync = fields.Boolean(
        "In Alerts",
        **CWEB_FIELD_ARGS,
        help="Partner is being synchronized with Companyweb. To remove from alerts, "
        "please contact Companyweb.",
    )
    cweb_sync_reference = fields.Char(
        **CWEB_FIELD_ARGS,
        index="btree_not_null",
        help="Identifies the record from Odoo with the one saved in the Alerts list at "
        "Companyweb",
    )

    # NL specific fields
    cweb_rsin_number_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_rsin_number = fields.Char(
        "Companyweb RSIN",
        **CWEB_FIELD_ARGS,
        help="RSIN: 'Rechtspersonen en Samenwerkingsverbanden "
        "Informatienummer' is used to exchange data with other government "
        "organisations, such as the Netherlands Tax Administration. "
        "(Netherlands only)",
    )
    cweb_liable_party_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_liable_party = fields.Text(
        "Liable Party",
        **CWEB_FIELD_ARGS,
        help="A 403 declaration is a liability statement in which the parent company "
        "accepts joint and several liability for the debts of its subsidiary. "
        "As a result, the subsidiary is not required; to publish its own annual "
        "accounts its figures are included in the consolidated financial "
        "statements of the parent company. (Netherlands only)",
    )

    # Cweb nested data fields (nested in a main data field of the response)
    cweb_currency_id = fields.Many2one(
        "res.currency", "Companyweb Currency", **CWEB_FIELD_ARGS
    )

    # Companystatus
    cweb_companystatus_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_companystatus = fields.Char(
        "Companyweb Status",
        **CWEB_FIELD_ARGS,
        help="Whether a company is active or not",
    )
    cweb_companystatus_code = fields.Char(
        "Companyweb Company StatusCode", **CWEB_FIELD_ARGS
    )

    # Address
    cweb_address_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_street = fields.Char(
        "Companyweb Street",
        **CWEB_FIELD_ARGS,
        help="Address of the registered office or headquarters",
    )
    cweb_zip = fields.Char("Companyweb Postal code", **CWEB_FIELD_ARGS)
    cweb_city = fields.Char("Companyweb City", **CWEB_FIELD_ARGS)
    cweb_country_code_address = fields.Char("Address Country Code", **CWEB_FIELD_ARGS)
    cweb_country_id = fields.Many2one(
        "res.country", "Companyweb Country", **CWEB_FIELD_ARGS
    )

    # Credit limit
    cweb_creditLimit_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_creditLimit = fields.Monetary(
        "Companyweb Credit Limit", currency_field="cweb_currency_id", **CWEB_FIELD_ARGS
    )
    cweb_creditLimit_unset = fields.Boolean(
        "Companyweb Credit Limit Unset", **CWEB_FIELD_ARGS
    )
    cweb_creditLimit_info = fields.Char("Credit Limit Info", **CWEB_FIELD_ARGS)
    cweb_warnings_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_warnings = fields.Text(
        "Warnings",
        **CWEB_FIELD_ARGS,
        help="Financial warning signs about the company",
    )

    # Balance
    cweb_startDate_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_startDate = fields.Date(
        "Established", **CWEB_FIELD_ARGS, help="Date of establishment of the company"
    )
    cweb_endDate_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_endDate = fields.Date(
        "End Date",
        **CWEB_FIELD_ARGS,
        help="Date at which the company stopped its activity",
    )
    cweb_score_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_score = fields.Char(
        "Companyweb Score",
        **CWEB_FIELD_ARGS,
        help="The Companyweb health barometer",
    )
    cweb_image = fields.Char("Companyweb Barometer Image", **CWEB_FIELD_ARGS)
    cweb_balance_data_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_balance_year = fields.Char("Book Year", **CWEB_FIELD_ARGS)
    cweb_closed_date = fields.Date("To Date", **CWEB_FIELD_ARGS)
    cweb_equityCapital = fields.Float("Equity", **CWEB_FIELD_ARGS)
    cweb_equityCapital_unset = fields.Boolean(
        "Companyweb Equity Capital Unset", **CWEB_FIELD_ARGS
    )
    cweb_average_fte = fields.Float("Average number of staff in FTE", **CWEB_FIELD_ARGS)
    cweb_average_fte_unset = fields.Boolean(
        "Companyweb Average number of staff in FTE Unset", **CWEB_FIELD_ARGS
    )
    cweb_addedValue = fields.Float("Profit/Loss of the Book Year", **CWEB_FIELD_ARGS)
    cweb_addedValue_unset = fields.Boolean(
        "Companyweb Gross Margin (+/-) Unset", **CWEB_FIELD_ARGS
    )
    cweb_turnover = fields.Float("Turnover", **CWEB_FIELD_ARGS)
    cweb_turnover_unset = fields.Boolean("Companyweb Turnover Unset", **CWEB_FIELD_ARGS)
    cweb_result = fields.Float("Gross Margin", **CWEB_FIELD_ARGS)
    cweb_result_unset = fields.Boolean("Gross Margin Unset", **CWEB_FIELD_ARGS)

    # Reports
    cweb_url_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_url = fields.Char(
        "Details",
        **CWEB_FIELD_ARGS,
        help="Further details about this company on companyweb.be",
    )
    cweb_url_report_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_url_report = fields.Char(
        "Commercial Report",
        **CWEB_FIELD_ARGS,
        help="Detailed report about this company on companyweb.be",
    )
    cweb_url_payment_experience_enable = fields.Boolean(**CWEB_FIELD_ARGS)
    cweb_url_payment_experience = fields.Char(
        "Payment Experience",
        **CWEB_FIELD_ARGS,
        help="A link to the payment experience report on companyweb.be",
    )

    # Helper fields
    cweb_show_button_address = fields.Boolean(
        "Companyweb Button Address Enabled", compute="_compute_cweb_show_button_address"
    )
    cweb_show_tab = fields.Boolean(
        "Companyweb Tab Enabled", compute="_compute_cweb_cweb_show_tab"
    )
    cweb_show_button_enhance = fields.Boolean(
        "Companyweb Button Enhance Enabled", compute="_compute_cweb_show_button_enhance"
    )
    cweb_image_tag = fields.Html(
        "Health Barometer",
        compute="_compute_cweb_image_tag",
    )

    # Config fields
    companyweb_followup_enable = fields.Boolean(
        compute="_compute_companyweb_followup_enable"
    )
    companyweb_sync_status = fields.Selection(
        [
            (CWEB_SYNC_STATUS_NONE, "None"),
            (CWEB_SYNC_STATUS_PENDING, "Pending"),
            (CWEB_SYNC_STATUS_ACTIVE, "Active"),
        ],
        "Alert Status",
        default=CWEB_SYNC_STATUS_NONE,
        readonly=True,
        copy=False,
    )

    @api.depends_context("company")
    @api.depends("company_id")
    def _compute_companyweb_followup_enable(self):
        env_company = self.env.company
        for partner in self:
            company = partner.company_id or env_company
            partner.companyweb_followup_enable = company.companyweb_followup_enable

    @api.depends("is_company", "vat", "country_id")
    def _compute_cweb_show_button_enhance(self):
        """
        Show button for type company if VAT starts with valid country code
        or valid country is set
        """
        for rec in self:
            rec.cweb_show_button_enhance = bool(
                rec.is_company
                and (
                    not rec.country_id
                    or (rec.vat and get_country_code_from_vat(rec.vat))
                    or rec.country_id.code in ALLOWED_COUNTRY_CODES
                )
            )

    @api.depends("cweb_image")
    def _compute_cweb_image_tag(self):
        for rec in self:
            cweb_image_tag = None
            if rec.cweb_image:
                path = f"companyweb_base/static/img/cweb_barometer/{rec.cweb_image}"
                try:
                    tools.misc.file_path(path)
                    cweb_image_tag = f'<img class="img-fluid" src="/{path}"/>'
                except FileNotFoundError:
                    _logger.warning("File not found: %s", path)
                    self.env["ir.logging"].sudo().create(
                        {
                            "name": _logger.name,
                            "type": "server",
                            "level": "WARNING",
                            "message": f"File not found: {path}",
                            "path": __name__,
                            "func": "_compute_cweb_image_tag",
                            "line": 0,
                        }
                    )
            rec.cweb_image_tag = cweb_image_tag

    @api.depends(*ADDRESS_FIELDS)
    def _compute_cweb_show_button_address(self):
        """for the button to be shown
        the partner has to have cweb_address enabled and data for the address field"""
        for rec in self:
            rec.cweb_show_button_address = all(rec[field] for field in ADDRESS_FIELDS)

    @api.depends(*get_all_enable_fields())
    def _compute_cweb_cweb_show_tab(self):
        """
        Show cweb tab if there's an error message or any of the enable fields is True
        """
        for rec in self:
            rec.cweb_show_tab = rec.cweb_error or any(
                rec[enable_field] for enable_field in get_all_enable_fields()
            )

    def _cweb_format(self, values):
        """
        In-place formatting of specific dict and M2O in values
        """
        # Transform values to M2O IDs
        values["cweb_prefLang_id"] = (
            lang_code := values.get("cweb_prefLang_id")
        ) and get_lang_id(self.env, lang_code)
        values["cweb_country_id"] = (
            country_code_address := values.get("cweb_country_code_address")
        ) and get_country_id(self.env, country_code_address)
        values["cweb_currency_id"] = (
            currency_name := values.get("cweb_currency_id")
        ) and get_currency_id(self.env, currency_name)

        # Transform Text and HTML
        values["cweb_warnings"] = (
            warnings := values.get("cweb_warnings")
        ) and format_warnings(warnings)
        values["cweb_main_industry"] = (
            main_industry := values.get("cweb_main_industry")
        ) and format_industry(main_industry)
        values["cweb_industries"] = (
            industries := values.get("cweb_industries")
        ) and "\n".join(format_industry(industry) for industry in industries)
        values["cweb_liable_party"] = (
            liable_party_dict := values.get("cweb_liable_party")
        ) and format_liable_party(liable_party_dict, self.env)
        values["cweb_peppol"] = bool(values["cweb_peppol"])

        # Transform Dates
        for field in DATE_FIELDS:
            values[field] = format_date(values[field])

        # Format floats and flag as set or unset
        for float_field in FLOAT_FIELDS:
            if float_field in values:
                value = format_float_value(values[float_field])
                values[float_field] = value
                values[f"{float_field}_unset"] = value is None

        return values

    def _cweb_parse(self, cweb_response):
        """
        Parse cweb data to odoo-field values
        """
        values = {
            "cweb_lastupdate": datetime.now(),
            **get_data_values(cweb_response),
            **get_nested_values(cweb_response),
            **get_balance_values(cweb_response),
        }
        values = self._cweb_format(values)
        return values

    def _cweb_populate(self, cweb_response):
        """
        Fill cweb fields
        """
        self.ensure_one()
        values = self._cweb_parse(cweb_response)
        if "cweb_sync" in values and values.get("cweb_sync", False):
            values["companyweb_sync_status"] = CWEB_SYNC_STATUS_ACTIVE
        self.write(values)

    def _get_cweb_credentials(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        url = IrConfigParameter.get_param("companyweb.alacarte", "")

        if "V2.0" not in url:
            raise exceptions.ValidationError(
                self.env._("Companyweb: Please use the address for API V2.0"),
            )

        login = self.env.company.cweb_login
        password = self.env.company.cweb_password
        lang = self.env.context.get("lang", self.env.user.lang)[:2].upper()
        if lang not in ["FR", "NL"]:
            lang = "EN"
        return url, login, password, lang

    def _cweb_call_get(self, args):
        """
        Raises:
            - Access error
        Returns:
            - Error
            - Search results
        """
        if not self.env.user.has_group("companyweb_base.cweb_download"):
            raise exceptions.AccessDenied(
                self.env._("Companyweb: You don't have access to download data")
            )
        error = ""
        url, login, password, lang = self._get_cweb_credentials()
        status, cweb_response = cweb_get(url, login, password, lang, args)
        if status == -1:
            error = self.env._(
                "Missing values for company search: %(message)s",
                message=cweb_response,
            )
        elif status != 0:
            error = self.env._(
                "Companyweb status %(status)i: %(message)s",
                status=status,
                message=cweb_response,
            )
        return error, cweb_response

    def _cweb_enhance(self):
        errors = []
        for partner in self:
            args = {}
            if partner.vat:
                args["vat"] = partner.vat
            if partner.company_registry:
                args["registry"] = partner.company_registry
            country_code = (
                partner.cweb_country_code
                or get_country_code_from_vat(partner.vat)
                or partner.country_id.code
            )
            if country_code:
                if country_code not in ALLOWED_COUNTRY_CODES:
                    errors.append(
                        self.env._(
                            "Companyweb only supports companies based in "
                            "%(country_codes)s",
                            country_codes=ALLOWED_COUNTRY_CODES,
                        )
                    )
                    continue
                args["country_code"] = country_code

            error, cweb_response = self._cweb_call_get(args)

            if error:
                partner.cweb_error = error
                errors.append(error)
            else:
                partner.cweb_error = False
                partner._cweb_populate(cweb_response)
        return errors

    def _cweb_copy_address(self):
        if not self.env.user.has_group("companyweb_base.cweb_view"):
            raise exceptions.AccessDenied(
                self.env._("Companyweb: You don't have access")
            )
        env_company = self.env.company
        for partner in self:
            company = partner.company_id or env_company
            for cweb_field, odoo_field in FILL_FIELD_MAP.items():
                if company[f"fill_{cweb_field}"]:
                    partner[odoo_field] = partner[cweb_field]
            partner.street2 = None
            partner.state_id = None

    @api.model
    def _cweb_ensure_credentials(self):
        return bool(self.env.company.cweb_login and self.env.company.cweb_password)

    def cweb_button_enhance(self):
        """
        Populate cweb fields from Companyweb
        """
        self.ensure_one()
        if not self.env.user.has_group("companyweb_base.cweb_download"):
            raise exceptions.AccessDenied(
                self.env._("Companyweb: You don't have access to download data")
            )
        if not self._cweb_ensure_credentials():
            return self._cweb_call_wizard_credentials()
        if not self.vat and not self.company_registry:
            return self._cweb_call_wizard_search()

        errors = self._cweb_enhance()
        if errors:
            msg = (
                errors[0]
                if len(errors) == 1
                else "\n".join(f"- {error}" for error in errors)
            )
            self.cweb_error = msg
            raise exceptions.ValidationError(msg)
        self.cweb_error = False
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._("Successfully fetched Companyweb data"),
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def cweb_button_copy_address(self):
        """
        Copy Companyweb data to res.partner fields
        """
        self.ensure_one()
        self._cweb_copy_address()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": self.env._("Copied Companyweb data to Contact"),
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            },
        }

    def _cweb_call_wizard_search(self):
        self.ensure_one()
        # Pass partner in context to trigger default_get and populate search terms
        wizard = (
            self.env["companyweb.search.wizard"]
            .with_context(default_partner_id=self.id)
            .create({})
        )
        # Do initial search
        return wizard.companyweb_search()

    @api.model
    def _cweb_call_wizard_credentials(self):
        self.ensure_one()
        wizard_form = self.env.ref("companyweb_base.companyweb_credential_wizard")
        return {
            "name": "Enter Companyweb Credentials",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "companyweb_base.credential_wizard_base",
            "view_id": wizard_form.id,
            "target": "new",
            "context": self.env.context,
        }

    def _push_followup_partners(self, partner_list):
        error = ""
        args = [{"AlertCompany": partner_list}]
        url, login, password, lang = self._get_cweb_credentials()
        status, cweb_response = cweb_push(url, login, password, lang, args)
        if status != 0:
            cweb_error = self.env._(
                "Companyweb error %(status)i: %(message)s",
                status=status,
                message=cweb_response,
            )
            return cweb_error, [], 0
        error_partners = (cweb_response.get("InvalidCompanies", {}) or {}).get(
            "InvalidAlertCompany", []
        )
        error_partner_dicts = [
            {
                "cweb_sync_reference": errp.get("Company", {}).get("Reference", False),
                "msg": errp.get("Message", ""),
            }
            for errp in error_partners
        ]
        num_partner_updated = cweb_response["NumberOfAlertsAddedOrUpdated"]
        return error, error_partner_dicts, num_partner_updated

    def action_push_followup_partners(self):
        """
        Add partners in self to a monitor-list on companyweb side.
        Changes to the list take effect the next day.
        1. Check partners have at least country and (vat or registry)
        2. Collect erroneous partners and leave error message on record
        3. Push valid partners
        4. Return notification for success and error
        5. If error, redirect to view of erroneous partners
        Raise:
            - Missing credentials
            - Cweb error
        Return:
            - Notification
            - View action if errors
        """
        if not self._cweb_ensure_credentials():
            raise exceptions.ValidationError(
                self.env._(
                    "Missing Companyweb credentials on company %(company)s",
                    company=self.env.company.name,
                )
            )
        partner_errors = self.env["res.partner"]
        partner_list = []
        for partner in self:
            vat = partner.vat or partner.cweb_vat
            registry = partner.company_registry or partner.cweb_registry
            country_code = (
                partner.cweb_country_code
                or get_country_code_from_vat(vat)
                or partner.country_id.code
            )
            if not (vat or registry):
                partner.cweb_error = self.env._("Missing VAT or Company Registry.")
                partner_errors |= partner
            elif not country_code:
                partner.cweb_error = self.env._("Missing country.")
                partner_errors |= partner
            elif country_code not in ALLOWED_COUNTRY_CODES:
                partner.cweb_error = self.env._(
                    "Invalid country. Countries supported: %(countries)s.",
                    countries=ALLOWED_COUNTRY_CODES,
                )
                partner_errors |= partner
            else:
                partner.cweb_error = False
                if not partner.cweb_sync_reference:
                    # Unique identifier to store on Companyweb side
                    partner.cweb_sync_reference = str(uuid4())
                partner_list.append(
                    {
                        "CountryCode": country_code,
                        "Identifier": vat or registry,
                        "IdentifierType": "VatNumber" if vat else "RegistrationNumber",
                        "Reference": partner.cweb_sync_reference,
                    }
                )

        cweb_error, error_partner_dicts, num_partner_updated = (
            self._push_followup_partners(partner_list)
        )
        if cweb_error:
            raise exceptions.ValidationError(cweb_error)
        for partner_dict in error_partner_dicts:
            if ref := partner_dict.get("cweb_sync_reference"):
                partner = self.search([("cweb_sync_reference", "=", ref)], limit=1)
                partner.cweb_error = partner_dict.get("msg")
                partner_errors |= partner

        msg = ""
        msg_append = self.env._(" to Companyweb Alerts.")
        if num_partner_updated:
            msg = self.env._(
                "Added %(num_partner)i contact(s)", num_partner=num_partner_updated
            )
        for success_partner in self - partner_errors:
            success_partner.companyweb_sync_status = CWEB_SYNC_STATUS_PENDING
        if partner_errors:
            if msg:
                msg += ". "
            msg += self.env._(
                "Failed to push %(num_partner_errors)i contact(s)",
                num_partner_errors=len(partner_errors),
            )
            action = partner_errors._get_records_action()
            action["name"] = "Failed contacts"
            params = {
                "type": "danger",
                "message": msg + msg_append,
                "sticky": True,
                "next": action,
            }
        else:
            params = {
                "type": "success",
                "message": msg + msg_append,
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "soft_reload",
                },
            }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": params,
        }

    @api.model
    def _cron_companyweb_followup(self):
        """
        Cron to catch any data that has changed on partners on the monitor-list
        -> Call for updated companies
        <- Receive companies and update them in Odoo
        -> Call for more companies and simultaneously confirm the companies received
            in last call
        ...
        1. Get updates from cweb
        2. Update Odoo
        3. Confirm updates to cweb (done in next call)
        4. If more updates remaining, repeat
        """
        Partner = self.env["res.partner"]
        if not self._cweb_ensure_credentials():
            raise exceptions.ValidationError(
                self.env._(
                    "Missing companyweb credentials on company %(company)s",
                    company=self.env.company.name,
                )
            )
        url, login, password, lang = self._get_cweb_credentials()
        updated_partners = []
        is_first_call = True
        while is_first_call or updated_partners:
            is_first_call = False
            status, cweb_response = cweb_sync(
                url, login, password, lang, updated_partners
            )
            if status != 0:
                raise exceptions.ValidationError(
                    self.env._(
                        "Companyweb error %(status)i while syncing: %(message)s",
                        status=status,
                        message=cweb_response,
                    )
                )
            remaining = (cweb_response.get("RemainingChanges", {}) or {}).get(
                "RemainingChangesCount", 0
            )
            partner_datas = (cweb_response["CompanyResponses"] or {}).get(
                "CompanyResponseV2_0", []
            )
            _logger.info(
                "Companyweb: Received %i contact(s) to update. Remaining: %i.",
                len(partner_datas),
                remaining,
            )
            self.env["ir.logging"].sudo().create(
                {
                    "name": _logger.name,
                    "type": "server",
                    "level": "INFO",
                    "message": (
                        f"Companyweb: Received {len(partner_datas)}"
                        f" contact(s) to update. Remaining: {remaining}."
                    ),
                    "path": __name__,
                    "func": "_cron_companyweb_followup",
                    "line": 0,
                }
            )

            updated_partners = []
            updated_existing_partners = []
            for partner_data in partner_datas:
                cweb_sync_reference = (
                    partner_data.get("FollowUpReference", {}) or {}
                ).get("Value", False)
                values = Partner._cweb_parse(partner_data)
                if cweb_sync_reference and (
                    partner := Partner.search(
                        [("cweb_sync_reference", "=", cweb_sync_reference)], limit=1
                    )
                ):
                    if "cweb_sync" in values and values.get("cweb_sync", False):
                        values["companyweb_sync_status"] = CWEB_SYNC_STATUS_ACTIVE
                    partner.write(values)
                    partner._cweb_copy_address()
                    updated_existing_partners.append(partner.id)

                # Confirm we treated all data received, even if no longer in DB
                # (so they are removed from the update list)
                # Sent to companyweb as confirmed in next call
                updated_partners.append(
                    {
                        "CountryCode": values.get("cweb_country_code"),
                        "RegistrationNumber": values.get("cweb_registry"),
                    }
                )
            if updated_existing_partners:
                _logger.info(
                    "Companyweb: Updated partners with IDs %s",
                    updated_existing_partners,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Companyweb: Updated partners with IDs"
                            f" {updated_existing_partners}"
                        ),
                        "path": __name__,
                        "func": "_cron_companyweb_followup",
                        "line": 0,
                    }
                )
            else:
                _logger.info("Companyweb: No matching partners found")
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": "Companyweb: No matching partners found",
                        "path": __name__,
                        "func": "_cron_companyweb_followup",
                        "line": 0,
                    }
                )
