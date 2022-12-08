# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

from freezegun import freeze_time
from vcr_unittest import VCRMixin

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestUpload(VCRMixin, TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestUpload, self).setUp(*args, **kwargs)
        self.demo_user = self.env.ref("base.user_demo")
        self.env.user.company_id.vat = False
        self.demo_user.partner_id.email = "test@odoo.com"
        self.demo_user.cweb_login = False
        self.demo_user.cweb_password = False

        self.env["account.move"].search(
            [
                ("payment_state", "=", "not_paid"),
                ("state", "=", "posted"),
                ("move_type", "in", ["out_invoice"]),
            ]
        ).button_draft()

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    def _init_security_group(self):
        group = self.env["res.groups"].search(
            [("id", "=", self.env.ref("companyweb_payment_info.cweb_upload").id)]
        )
        add_user = [(4, self.demo_user.id)]
        group.write({"users": add_user})

    def _init_company_vat(self):

        self.env.user.company_id.vat = "BE0835207216"

    def _init_cweb_credentials(self):
        self.demo_user.cweb_login = os.environ.get(
            "COMPANYWEB_TEST_LOGIN", "cwebtestlogin"
        )
        self.demo_user.cweb_password = os.environ.get(
            "COMPANYWEB_TEST_PASSWORD", "cwebtestpassword"
        )

    def _init_invoice(self):
        Partner = self.env["res.partner"].with_user(self.demo_user)
        self.p1 = Partner.create(
            {
                "name": "Bisnode SA",
                "vat": "BE0458.662.817",
            }
        )
        self.out_invoice_1 = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "date": "2022-01-13",
                "invoice_date": "2022-01-13",
                "partner_id": self.p1.id,
                "currency_id": self.env.user.company_id.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_25").id,
                            "price_unit": 1000.0,
                        },
                    )
                ],
            }
        )
        self.out_invoice_1.action_post()

    @freeze_time("2022-01-13")  # because the login hash includes the date
    def test_upload_payment(self):

        # UserError because of security
        with self.assertRaises(UserError):
            self.env["companyweb_payment_info.payment_info_wizard"].with_user(
                self.demo_user
            )._cweb_payment_info_step1()

        self._init_security_group()

        # UserError no vat on users's company
        with self.assertRaises(UserError):
            self.env["companyweb_payment_info.payment_info_wizard"].with_user(
                self.demo_user
            )._cweb_payment_info_step1()

        self.env.user.company_id.vat = "FR0835207216"

        # UserError bad on users's company
        with self.assertRaises(UserError):
            self.env["companyweb_payment_info.payment_info_wizard"].with_user(
                self.demo_user
            )._cweb_payment_info_step1()

        self._init_company_vat()

        # UserError credentials
        result_no_credentials = (
            self.env["companyweb_payment_info.payment_info_wizard"]
            .with_user(self.demo_user)
            ._cweb_payment_info_step1()
        )
        self.assertEqual(
            result_no_credentials["res_model"],
            "companyweb_payment_info.credential_wizard_payment",
        )
        self._init_cweb_credentials()

        # UserError No invoice to send
        with self.assertRaises(UserError):
            self.env["companyweb_payment_info.payment_info_wizard"].with_user(
                self.demo_user
            )._cweb_payment_info_step1()

        self._init_invoice()

        res = (
            self.env["companyweb_payment_info.payment_info_wizard"]
            .with_user(self.demo_user)
            ._cweb_payment_info_step1()
        )
        res_wizard1 = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(res_wizard1.wizard_step, "step2")

        res = (
            self.env["companyweb_payment_info.payment_info_wizard"]
            .with_user(self.demo_user)
            ._cweb_payment_info_step2()
        )
        res_wizard2 = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(res_wizard2.wizard_step, "step3")
