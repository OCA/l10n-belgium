# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import TestVatReportsCommon


class TestVatListing(TestVatReportsCommon):
    def _get_tax(self):
        return self.env.ref("l10n_be.%s_attn_VAT-OUT-21-S" % self.env.company.id)

    def setUp(self):
        super().setUp()
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

    def test_xml_list(self):
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()
        xml = self._get_xml_from_report_action(partner_vat_list.create_xml())
        ns = {"ns2": "http://www.minfin.fgov.be/ClientListingConsignment"}
        node = xml.xpath("//ns2:ClientListing", namespaces=ns)[0]
        xml_total_turnover = node.attrib["TurnOverSum"]
        xml_total_vat = node.attrib["VATAmountSum"]
        self.assertEqual(xml_total_turnover, "450.00")
        self.assertEqual(xml_total_vat, "94.50")

    def test_vat_listing_ignore_invalid_invoices(self):
        invoice_tax = self._get_tax()
        # create a draft invoice
        self._create_test_invoice(invoice_tax)
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
        self.partner.flush_recordset()
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()
        self.assertEqual(partner_vat_list.total_turnover, 450.0)
        self.assertEqual(partner_vat_list.total_vat, 94.5)
