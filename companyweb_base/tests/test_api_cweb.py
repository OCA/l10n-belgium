# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# API documentation : https://docs.companyweb.be

import os
from datetime import datetime

import requests
from freezegun import freeze_time
from requests import PreparedRequest, Session
from vcr_unittest import VCRMixin

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon

_super_send = requests.Session.send
from urllib import parse


class TestApiCweb(VCRMixin, BaseCommon):
    @classmethod
    def _request_handler(cls, s: Session, r: PreparedRequest, /, **kw):
        """
        Override to allow requests to the companyweb API
        because Odoo only permits calls to localhost
        (see https://github.com/odoo/odoo/blob/17.0/odoo/tests/common.py#L265 )
        """
        url = parse.urlparse(r.url)
        if url.hostname == "connect.companyweb.be":
            return _super_send(s, r, **kw)
        return super()._request_handler(s=s, r=r, **kw)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        french = cls.env.ref("base.lang_fr")
        french.install_lang()
        french.active = True

        cls.cwb_user = new_test_user(
            cls.env, "cwb_user", "companyweb_base.cweb_download"
        )

        cls.cwb_user.cweb_login = os.environ.get(
            "COMPANYWEB_TEST_LOGIN", "cwebtestlogin"
        )
        cls.cwb_user.cweb_password = os.environ.get(
            "COMPANYWEB_TEST_PASSWORD", "cwebtestpassword"
        )

        Partner = cls.env["res.partner"]
        cls.p1 = Partner.create(
            {
                "name": "Acsone SA",
                "vat": "BE0405056855",
            }
        )

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query", "raw_body"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    @freeze_time("2021-03-23")  # because the login hash includes the date
    def test_cweb_button(self):
        # companyweb response depends on request language
        # we force the language so we know what to expect in the response
        self.p1.with_user(self.cwb_user).with_context(
            lang="fr_FR"
        ).cweb_button_enhance()
        self.assertTrue(self.p1.cweb_prefLang_enable)
        self.assertEqual(self.p1.cweb_prefLang_id, self.env.ref("base.lang_nl"))
        self.assertTrue(self.p1.cweb_name_enable, "test cweb name KO")
        self.assertEqual(
            self.p1.cweb_name, "Scheerders van Kerchove's Verenigde Fabrieken"
        )
        self.assertTrue(self.p1.cweb_jur_form_enable)
        self.assertEqual(self.p1.cweb_jur_form, "SA")
        self.assertTrue(self.p1.cweb_address_enable)
        self.assertEqual(self.p1.cweb_street, "Aerschotstraat 114")
        self.assertEqual(self.p1.cweb_zip, "9100")
        self.assertEqual(self.p1.cweb_city, "Sint-Niklaas")
        self.assertEqual(self.p1.cweb_country_id.code.upper(), "BE")
        self.assertTrue(self.p1.cweb_companystatus_enable)
        self.assertEqual(self.p1.cweb_companystatus, "Actif")
        self.assertEqual(self.p1.cweb_companystatus_code, "0")
        self.assertTrue(self.p1.cweb_startDate_enable)
        self.assertEqual(
            self.p1.cweb_startDate, datetime.strptime("19280929", "%Y%m%d").date()
        )
        self.assertTrue(self.p1.cweb_endDate_enable)
        self.assertFalse(self.p1.cweb_endDate)
        self.assertTrue(self.p1.cweb_score_enable)
        self.assertEqual(self.p1.cweb_score, "3")
        self.assertEqual(self.p1.cweb_image, "pos-03.png")
        self.assertTrue(self.p1.cweb_creditLimit_unset)
        self.assertTrue(self.p1.cweb_creditLimit_enable)
        self.assertEqual(self.p1.cweb_creditLimit, 1321000)
        self.assertFalse(self.p1.cweb_creditLimit_info)
        self.assertTrue(self.p1.cweb_warnings_enable)
        # Note : as the warnings are transformed, i can't check the value exactly
        self.assertTrue(self.p1.cweb_warnings)
        self.assertTrue(self.p1.cweb_url_enable)
        self.assertEqual(
            self.p1.cweb_url, "https://www.companyweb.be/company/405056855"
        )
        self.assertTrue(self.p1.cweb_url_report_enable)
        self.assertEqual(
            self.p1.cweb_url_report,
            "https://reporting.companyweb.be/rappLoad.asp?"
            "lang=F&login=ACSONESOAP&vat=405056855&key=12604a43a7fd63ee823752b8d9c2fd31",
        )
        self.assertTrue(self.p1.cweb_balance_data_enable)
        self.assertEqual(self.p1.cweb_balance_year, "2019")
        self.assertEqual(
            self.p1.cweb_closed_date, datetime.strptime("2019-12-31", "%Y-%m-%d").date()
        )
        self.assertTrue(self.p1.cweb_equityCapital_unset)
        self.assertEqual(self.p1.cweb_equityCapital, 23086258)
        self.assertEqual(self.p1.cweb_addedValue, 41206)
        self.assertTrue(self.p1.cweb_addedValue_unset)
        self.assertEqual(self.p1.cweb_result, 18226650)
        self.assertTrue(self.p1.cweb_result_unset)
        self.assertEqual(self.p1.cweb_turnover, 46825985)
        self.assertTrue(self.p1.cweb_turnover_unset)

        self.p1.with_user(self.cwb_user).with_context(
            lang="fr_FR"
        ).cweb_button_copy_address()
        self.assertEqual(self.p1.street, self.p1.cweb_street)
        self.assertEqual(self.p1.city, self.p1.cweb_city)
        self.assertEqual(self.p1.zip, self.p1.cweb_zip)
        self.assertEqual(self.p1.country_id, self.p1.cweb_country_id)
        self.assertFalse(self.p1.street2)
        self.assertFalse(self.p1.state_id.code)
