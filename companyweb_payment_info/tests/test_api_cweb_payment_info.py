# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# API documentation: https://docs.companyweb.be
# For cassette instructions, see companyweb_base/tests/common.py.

from unittest.mock import patch

from freezegun import freeze_time

from odoo.tools import mute_logger

from odoo.addons.companyweb_base.tests.common import CwebTestCommon

PAYEX_URL = "https://autopayex.companyweb.be/v4.0/AutoPayex.asmx"


class TestApiCwebPaymentInfo(CwebTestCommon):
    CWEB_ALLOWED_HOSTNAMES = ("autopayex.companyweb.be",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company.write(
            {
                "country_id": cls.env.ref("base.be").id,
                "company_registry": "0869703978",
            }
        )
        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer BE",
                "is_company": True,
                "country_id": cls.env.ref("base.be").id,
                "company_registry": "0405056855",
            }
        )

    def _set_credentials(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "companyweb.payex.url", PAYEX_URL
        )
        return super()._set_credentials()

    def _create_open_invoice(
        self, partner=None, amount=1000.0, invoice_date="2026-06-01"
    ):
        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company.id)], limit=1
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": (partner or self.customer).id,
                "journal_id": journal.id,
                "invoice_date": invoice_date,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {"name": "Test Service", "quantity": 1, "price_unit": amount},
                    )
                ],
            }
        )
        invoice.action_post()
        return invoice

    @freeze_time("2026-07-03")
    def test_cron_send_open_invoices(self):
        self._set_credentials()
        self.company.companyweb_payment_info_enable = True
        invoice = self._create_open_invoice()
        self.assertEqual(invoice.payment_state, "not_paid")

        vals = invoice._cweb_prepare_invoice_values()
        self.assertEqual(vals["InvoiceNumber"], invoice.name)
        self.assertEqual(vals["InvoiceDate"], "20260601")
        self.assertEqual(vals["CustomerCountry"], "BE")
        self.assertEqual(vals["CustomerIdentifierType"], "RegistrationNumber")
        self.assertEqual(vals["CustomerIdentifier"], self.customer.company_registry)
        self.assertEqual(vals["OpenAmountWhole"], str(int(invoice.amount_residual)))

        self.env["account.move"]._cron_cweb_send_open_invoices()

    def test_prepare_invoice_skips_missing_identifier(self):
        partner = self.env["res.partner"].create(
            {
                "name": "No ID Customer",
                "is_company": True,
                "country_id": self.env.ref("base.be").id,
            }
        )
        invoice = self._create_open_invoice(partner=partner)
        self.assertIsNone(invoice._cweb_prepare_invoice_values())

    def test_prepare_invoice_skips_unsupported_country(self):
        partner = self.env["res.partner"].create(
            {
                "name": "UK Customer",
                "is_company": True,
                "country_id": self.env.ref("base.uk").id,
                "company_registry": "12345678",
            }
        )
        invoice = self._create_open_invoice(partner=partner)
        self.assertIsNone(invoice._cweb_prepare_invoice_values())

    @patch(
        "odoo.addons.companyweb_payment_info.models.account_move.cweb_send_open_invoices"
    )
    def test_cron_skips_disabled_company(self, mock_send):
        self._set_credentials()
        self.company.companyweb_payment_info_enable = False
        self._create_open_invoice()
        self.env["account.move"]._cron_cweb_send_open_invoices()
        mock_send.assert_not_called()

    @mute_logger("odoo.addons.companyweb_payment_info.models.account_move")
    @patch(
        "odoo.addons.companyweb_payment_info.models.account_move.cweb_send_open_invoices"
    )
    def test_cron_skips_missing_credentials(self, mock_send):
        self.env["ir.config_parameter"].sudo().set_param(
            "companyweb.payex.url", PAYEX_URL
        )
        self.company.companyweb_payment_info_enable = True
        self.company.cweb_login = False
        self.company.cweb_password = False
        self._create_open_invoice()
        self.env["account.move"]._cron_cweb_send_open_invoices()
        mock_send.assert_not_called()
