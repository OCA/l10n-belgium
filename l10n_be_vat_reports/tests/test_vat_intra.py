# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import time

from .common import TestVatReportsCommon


class TestVatIntra(TestVatReportsCommon):
    def _get_tax(self):
        return self.env.ref("l10n_be.%s_attn_VAT-OUT-00-EU-S" % self.env.company.id)

    def setUp(self):
        super().setUp()
        self._create_test_data(self._get_tax())

    def test_xml_list(self):
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        xml = self._get_xml_from_report_action(wizard.create_xml())
        ns = {"ns2": "http://www.minfin.fgov.be/IntraConsignment"}
        xml_vat_amount = xml.xpath("//ns2:IntraListing", namespaces=ns)[0].attrib[
            "AmountSum"
        ]
        codes = xml.xpath("//ns2:IntraListing/ns2:IntraClient/ns2:Code", namespaces=ns)
        for code in codes:
            self.assertTrue(code.text)
        self.assertEqual(xml_vat_amount, "450.00")

    def test_pdf_list(self):
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        self.assertEqual(wizard.client_ids[0].amount, 450.0)
        self.assertEqual(wizard.amount_total, 450.0)
        wizard.print_vat_intra()

    def test_intra_ignore_invalid_invoices(self):
        invoice_tax = self._get_tax()
        # create a draft invoice
        self._create_test_invoice(invoice_tax)
        cancelled_invoice = self._create_test_invoice(invoice_tax)
        cancelled_invoice.button_cancel()
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        # draft and cancelled invoices must be ignored
        self.assertEqual(wizard.client_ids[0].amount, 450.0)
        self.assertEqual(wizard.amount_total, 450.0)

    def test_intra_include_archived_partners(self):
        self.partner.active = False
        # ensure change is done in the database
        self.partner.flush_recordset()
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        self.assertEqual(wizard.client_ids[0].amount, 450.0)
        self.assertEqual(wizard.amount_total, 450.0)
