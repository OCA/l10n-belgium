# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# API documentation: https://docs.companyweb.be

import os
from unittest.mock import patch

from freezegun import freeze_time

from odoo import exceptions
from odoo.tests import Form, new_test_user, users

from ..cweb_const import FILL_FIELD_MAP
from ..models.res_partner import (
    CWEB_SYNC_STATUS_ACTIVE,
    CWEB_SYNC_STATUS_NONE,
    CWEB_SYNC_STATUS_PENDING,
)
from .common import TEST_LOGIN, TEST_PASSWORD, CwebTestCommon

# Values saved in cassette. We don't test
# - dates (FakeDates)
# - related record IDs (which might differ to demo DB)
# - URL with varying tokens
EXPECTED_VALUES = {
    "cweb_addedValue": -20251636.08,
    "cweb_addedValue_unset": False,
    "cweb_address_enable": True,
    "cweb_average_fte": 128.7,
    "cweb_average_fte_unset": False,
    "cweb_balance_data_enable": True,
    "cweb_balance_year": "2024",
    "cweb_city": "Sint-Niklaas",
    "cweb_companystatus": "Actif",
    "cweb_companystatus_code": "0",
    "cweb_companystatus_enable": True,
    "cweb_creditLimit": 0,
    "cweb_creditLimit_enable": True,
    "cweb_creditLimit_info": "Résultat très négatif",
    "cweb_creditLimit_unset": False,
    "cweb_email": "info@svk.be",
    "cweb_email_enable": True,
    "cweb_endDate": False,
    "cweb_endDate_enable": True,
    "cweb_equityCapital": 7533441.94,
    "cweb_equityCapital_unset": False,
    "cweb_image": "neg-34.png",
    "cweb_jur_form": "SA",
    "cweb_jur_form_enable": True,
    "cweb_main_industry_enable": True,
    "cweb_name": "Scheerders van Kerchove's Verenigde Fabrieken",
    "cweb_name_enable": True,
    "cweb_phone": "037604900",
    "cweb_phone_enable": True,
    "cweb_prefLang_enable": True,
    "cweb_registry": "0405056855",
    "cweb_registry_enable": True,
    "cweb_result": 8485555.32,
    "cweb_result_unset": False,
    "cweb_score": "-34",
    "cweb_score_enable": True,
    "cweb_startDate_enable": True,
    "cweb_street": "Aerschotstraat 114",
    "cweb_turnover": 27246603.74,
    "cweb_turnover_unset": False,
    "cweb_url": "https://www.companyweb.be/fr/c/0405056855/svk",
    "cweb_url_enable": True,
    "cweb_url_report_enable": True,
    "cweb_vat": "BE 0405.056.855",
    "cweb_vat_enable": True,
    "cweb_vat_liable": True,
    "cweb_vat_liable_enable": True,
    "cweb_warnings_enable": True,
    "cweb_website": "https://svk.be",
    "cweb_website_enable": True,
    "cweb_zip": "9100",
    "cweb_commercial_name": False,
    "cweb_commercial_name_enable": True,
    "cweb_country_code": "BE",
    "cweb_industries": "23650 - Fabrication d’ouvrages en fibre-ciment\n"
    "23650 - Fabrication d’ouvrages en fibre-ciment\n"
    "18120 - Autres activités d’imprimerie\n"
    "23321 - Fabrication de briques",
    "cweb_industries_enable": True,
    "cweb_liable_party": False,
    "cweb_liable_party_enable": False,
    "cweb_main_industry": "23650 - Fabrication d’ouvrages en fibre-ciment",
    "cweb_peppol": True,
}


class TestApiCweb(CwebTestCommon):
    CWEB_ALLOWED_HOSTNAMES = ("connect.companyweb.be",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        french = cls.env.ref("base.lang_fr")
        french.install_lang()
        french.active = True
        cls.belgium = cls.env.ref("base.be")
        cls.france = cls.env.ref("base.fr")
        cls.normal_user = new_test_user(
            cls.env, "normal_user", "base.group_partner_manager"
        )
        cls.cwb_user = new_test_user(
            cls.env, "cwb_user", "companyweb_base.cweb_download"
        )
        # Results are language-dependent
        cls.cwb_user.lang = "FR"

    def _enable_followup(self):
        self.company.write({"companyweb_followup_enable": True})
        self.assertTrue(self.company.companyweb_followup_enable)

    def _create_partner(self, values=None):
        if values is None:
            # Partner data in cassette and EXPECTED_VALUES
            values = {
                "name": "Test",
                "vat": "BE0405056855",
            }
        values.update({"is_company": True})
        return self.env["res.partner"].create(values)

    def test_ensure_credentials(self):
        self._set_credentials()
        self.assertTrue(self.env["res.partner"]._cweb_ensure_credentials())

    @users("normal_user")
    def test_cweb_access(self):
        self._set_credentials()
        partner = self._create_partner()
        with self.assertRaisesRegex(
            exceptions.AccessDenied,
            "Companyweb: You don't have access to download data",
        ):
            partner.cweb_button_enhance()

    @users("cwb_user")
    def test_api2(self):
        self._set_credentials()
        self.env["ir.config_parameter"].sudo().set_param(
            "companyweb.alacarte",
            "https://connect.companyweb.be/V1.3/alacarteservice.asmx",
        )
        partner = self._create_partner()
        with self.assertRaisesRegex(
            exceptions.ValidationError,
            "Companyweb: Please use the address for API V2.0",
        ):
            partner.cweb_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_credentials_wizard(self):
        login = os.environ.get("COMPANYWEB_TEST_LOGIN", TEST_LOGIN)
        password = os.environ.get("COMPANYWEB_TEST_PASSWORD", TEST_PASSWORD)
        partner = self._create_partner(
            {
                "name": "Acsone SA",
            }
        )
        action = partner.cweb_button_enhance()
        # Credentials wizard got returned
        self.assertEqual(
            action.get("res_model"), "companyweb_base.credential_wizard_base"
        )

        credentials_wizard = Form.from_action(self.env, action)
        credentials_wizard.cweb_login = login
        credentials_wizard.cweb_password = password
        credentials_wizard.save()
        credentials_wizard.record.with_context(
            active_id=partner.id
        ).save_cweb_login_pwd()
        self.assertEqual(self.company.cweb_login, login)
        self.assertEqual(self.company.cweb_password, password)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_button_vat(self):
        self._set_credentials()
        partner = self._create_partner()
        self.assertTrue(partner.cweb_show_button_enhance)
        result = partner.cweb_button_enhance()
        self.assertEqual(result.get("params", {}).get("type"), "success")
        self.assertTrue(partner.cweb_show_button_address)
        self.assertTrue(partner.cweb_show_tab)
        for cweb_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[cweb_field], expected_result)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_button_registry(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0405056855",
                "country_id": self.belgium.id,
            }
        )
        self.assertTrue(partner.cweb_show_button_enhance)
        partner.cweb_button_enhance()
        for cweb_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[cweb_field], expected_result)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_button_search(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Scheerders van Kerchoves Verenigde Fabrieken",
                "country_id": self.belgium.id,
            }
        )
        self.assertTrue(partner.cweb_show_button_enhance)
        action = partner.cweb_button_enhance()

        # Search wizard got returned
        self.assertEqual(action.get("res_model"), "companyweb.search.wizard")
        wizard = self.env["companyweb.search.wizard"].browse(action.get("res_id"))
        self.assertTrue(len(wizard.line_ids) > 0)
        first_result = wizard.line_ids[0]
        first_result.select()
        for cweb_field, expected_result in EXPECTED_VALUES.items():
            self.assertEqual(partner[cweb_field], expected_result)

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_button_search_missing_values(self):
        """
        Test missing country and missing country code in VAT
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "0405056855",
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "Missing values for company search"
        ):
            partner.cweb_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_button_wrong_vat(self):
        """
        Test invalid VAT (cweb error)
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "123123123",
                "country_id": self.belgium.id,
            }
        )
        with self.assertRaisesRegex(exceptions.ValidationError, "Companyweb status"):
            partner.cweb_button_enhance()

    @users("cwb_user")
    def test_cweb_button_wrong_country(self):
        """
        Test invalid country
        """
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0405056855",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "Companyweb only supports companies based in"
        ):
            partner.cweb_button_enhance()

    @users("cwb_user")
    @freeze_time("2026-01-29")
    def test_cweb_copy_data(self):
        self._set_credentials()
        disabled_fields = [
            "fill_cweb_street",
            "fill_cweb_zip",
            "fill_cweb_city",
            "fill_cweb_country_id",
        ]
        self.company.sudo().write(
            {disabled_field: False for disabled_field in disabled_fields}
        )
        partner = self._create_partner()
        partner.cweb_button_enhance()
        result = partner.cweb_button_copy_address()
        self.assertEqual(result.get("params", {}).get("type"), "success")

        for cweb_field, odoo_field in FILL_FIELD_MAP.items():
            # Disabled fields are not copied
            if f"fill_{cweb_field}" in disabled_fields:
                self.assertNotEqual(partner[cweb_field], partner[odoo_field])
            else:
                self.assertEqual(partner[cweb_field], partner[odoo_field])
        self.company.sudo().write(
            {disabled_field: True for disabled_field in disabled_fields}
        )
        partner.cweb_button_copy_address()
        for cweb_field, odoo_field in FILL_FIELD_MAP.items():
            # All fields are copied
            self.assertEqual(partner[cweb_field], partner[odoo_field])

    @users("normal_user")
    @freeze_time("2026-01-29")
    def test_access_copy_data(self):
        partner = self._create_partner()
        partner.with_user(self.cwb_user).cweb_button_enhance()
        with self.assertRaisesRegex(
            exceptions.AccessDenied, "Companyweb: You don't have access"
        ):
            partner.cweb_button_copy_address()

    @users("cwb_user")
    @freeze_time("2026-02-10")
    def test_cweb_push(self):
        self._set_credentials()
        self._enable_followup()
        partner = self._create_partner()
        self.assertTrue(partner.companyweb_followup_enable)
        partner.cweb_button_enhance()
        result = partner.action_push_followup_partners()
        msg = result.get("params").get("message")
        self.assertEqual(partner.companyweb_sync_status, CWEB_SYNC_STATUS_PENDING)
        self.assertIn("Added 1 contact(s)", msg)

    @freeze_time("2026-03-06")
    def test_cweb_cron(self):
        self._set_credentials()
        self._enable_followup()
        # Use specific details pushed manually and saved in cassette.
        # We don't push in this test
        partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "0878194448",
                "country_id": self.belgium.id,
                "cweb_sync_reference": "38b9ef0a-8c8a-4c53-852e-d413470be836",
            }
        )
        self.assertEqual(partner.companyweb_sync_status, CWEB_SYNC_STATUS_NONE)
        self.env["res.partner"]._cron_companyweb_followup()
        self.assertEqual(partner.companyweb_sync_status, CWEB_SYNC_STATUS_ACTIVE)
        # Ensure new partner data has been filled to contact
        self.assertEqual(partner.name, partner.cweb_name)

    @users("cwb_user")
    @freeze_time("2026-03-10")
    def test_cweb_push_multi(self):
        self._set_credentials()
        self._enable_followup()
        valid_partner = self._create_partner()
        # Use specific ref saved in cassette.
        invalid_partner = self._create_partner(
            {
                "name": "Test",
                "company_registry": "123123123",
                "country_id": self.belgium.id,
                "cweb_sync_reference": "38b9ef0a-8c8a-4c53-852e-d413470be836",
            }
        )
        result = (valid_partner | invalid_partner).action_push_followup_partners()
        msg = result.get("params").get("message")
        self.assertIn("Added 1 contact(s)", msg)
        self.assertIn("Failed to push 1 contact(s)", msg)
        self.assertIn("n’est pas un numero de registration", invalid_partner.cweb_error)

    def test_push_uses_vat_country_not_address_country(self):
        """
        A Belgian partner (BE VAT) with a Dutch address must send CountryCode=BE
        to the alerts API, not NL from the address.
        """
        self._set_credentials()
        self._enable_followup()
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "BE0405056855",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        pushed_lists = []

        def mock_push(self_inner, partner_list):
            pushed_lists.append(partner_list)
            return "", [], 1

        with patch.object(type(partner), "_push_followup_partners", mock_push):
            partner.action_push_followup_partners()

        self.assertEqual(len(pushed_lists), 1)
        self.assertEqual(len(pushed_lists[0]), 1)
        self.assertEqual(pushed_lists[0][0]["CountryCode"], "BE")

    def test_enhance_uses_vat_country_not_address_country(self):
        """
        A partner with a Belgian VAT but an address in a non-allowed country (UK)
        must not be rejected during enhance — the country is determined from the VAT,
        not the address.
        """
        partner = self._create_partner(
            {
                "name": "Test",
                "vat": "BE0405056855",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        called_args = []

        def mock_call_get(self_inner, args):
            called_args.append(dict(args))
            return "mocked", None

        with patch.object(type(partner), "_cweb_call_get", mock_call_get):
            errors = partner._cweb_enhance()

        self.assertTrue(called_args, "API call should have been attempted")
        self.assertEqual(called_args[0].get("country_code"), "BE")
        self.assertFalse(
            any("only supports companies" in (e or "") for e in errors),
            "Partner must not be rejected due to address country",
        )

    def test_nl_fields(self):
        self._set_credentials()
        nl_partner = self._create_partner(
            {
                "name": "Test",
                "vat": "NL 810433941 B01",
            }
        )
        nl_partner.cweb_button_enhance()
        self.assertTrue(nl_partner.cweb_rsin_number_enable)
        self.assertTrue(nl_partner.cweb_liable_party_enable)
        self.assertEqual(
            nl_partner.cweb_liable_party,
            "Coolblue Holding (NL)\nVAT: NL 810437466 B01\nEst. 01/01/2014",
        )
        self.assertEqual(nl_partner.cweb_rsin_number, "810433941")

    @users("cwb_user")
    @freeze_time("2026-07-02")
    def test_cweb_button_vat_fr(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test FR",
                "vat": "FR51306138900",
            }
        )
        self.assertTrue(partner.cweb_show_button_enhance)
        result = partner.cweb_button_enhance()
        self.assertEqual(result.get("params", {}).get("type"), "success")
        self.assertTrue(partner.cweb_show_tab)
        self.assertEqual(partner.cweb_country_code, "FR")

    @users("cwb_user")
    @freeze_time("2026-07-02")
    def test_cweb_button_registry_fr(self):
        self._set_credentials()
        partner = self._create_partner(
            {
                "name": "Test FR",
                "company_registry": "652014051",
                "country_id": self.france.id,
            }
        )
        self.assertTrue(partner.cweb_show_button_enhance)
        partner.cweb_button_enhance()
        self.assertEqual(partner.cweb_country_code, "FR")
