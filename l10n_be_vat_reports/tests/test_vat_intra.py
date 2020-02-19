# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.report.models import report

from lxml.etree import XML
import unittest
import time

from .common import TestVatReportsCommon


class TestVatIntra(TestVatReportsCommon):
    def setUp(self):
        super(TestVatReportsCommon, self).setUp()
        company = self.env.user.company_id
        tax = self.env.ref("l10n_be.%s_attn_VAT-OUT-00-EU-S" % company.id)
        self._create_test_data(tax)

    def test_xml_list(self):
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),  # todo use native date
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.create_xml()
        ns = {"ns2": "http://www.minfin.fgov.be/IntraConsignment"}
        xml = XML(wizard.file_save.decode("base64"))
        xml_vat_amount = xml.xpath("//ns2:IntraListing", namespaces=ns)[
            0
        ].attrib["AmountSum"]
        codes = xml.xpath(
            "//ns2:IntraListing/ns2:IntraClient/ns2:Code", namespaces=ns
        )
        for code in codes:
            self.assertTrue(code.text)
        self.assertEqual("450.00", xml_vat_amount)

    @unittest.skipIf(
        report.wkhtmltopdf_state == "install", "wkhtmltopdf not available"
    )
    def test_pdf_list(self):
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),  # todo use native date
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        # todo  If you need to generate a PDF in tests, you have to pass the context key force_report_rendering=True for getting that instead of an HTML, as now the method qweb_render_pdf defaults to qweb_render_html on test environment.
        report_action = wizard.preview()
        self.env["report"].get_pdf(
            [], report_action["report_name"], data=report_action["data"]
        )
