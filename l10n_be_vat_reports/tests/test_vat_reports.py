# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import TestVatReportsCommon


class TestVatListing(TestVatReportsCommon):
    def _get_tax(self):
        company = self.env.company
        return self.env.ref("l10n_be.%s_attn_VAT-OUT-21-S" % company.id)

    def setUp(self):
        super().setUp()
        company = self.env.company
        self._create_test_data(self._get_tax())

    def test_partner_vat_listing(self):
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()

        self.assertEqual(partner_vat_list.total_turnover, 450.0)
        self.assertEqual(partner_vat_list.total_vat, 94.5)

        # coverage
        partner_vat_list.create_xml()
        partner_vat_list.print_vatlist()

    def test_vat_listing_ignore_invalid_invoices(self):
        invoice_tax = self._get_tax()
        draft_invoice = self._create_test_invoice(invoice_tax)
        cancelled_invoice = self._create_test_invoice(invoice_tax)
        cancelled_invoice.button_cancel()
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()
        # draft and cancelled invoices must be ignored
        self.assertEqual(partner_vat_list.total_turnover, 450.0)
        self.assertEqual(partner_vat_list.total_vat, 94.5)

    def test_vat_listing_include_archived_partners(self):
        self.partner.active = False
        # ensure change is done in the database
        self.partner.flush()
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()
        self.assertEqual(partner_vat_list.total_turnover, 450.0)
        self.assertEqual(partner_vat_list.total_vat, 94.5)
