# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from lxml.etree import XML
import base64
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
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        wizard.create_xml()
        ns = {"ns2": "http://www.minfin.fgov.be/IntraConsignment"}
        xml = XML(base64.b64decode(wizard.file_save))
        xml_vat_amount = xml.xpath("//ns2:IntraListing", namespaces=ns)[
            0
        ].attrib["AmountSum"]
        codes = xml.xpath(
            "//ns2:IntraListing/ns2:IntraClient/ns2:Code", namespaces=ns
        )
        for code in codes:
            self.assertTrue(code.text)
        self.assertEqual("450.00", xml_vat_amount)

    def test_pdf_list(self):
        wizard = self.env["partner.vat.intra"].create(
            {
                "period_code": time.strftime("00%Y"),
                "date_start": time.strftime("%Y-01-01"),
                "date_end": time.strftime("%Y-12-31"),
            }
        )
        wizard.get_partners()
        self.assertEquals(wizard.client_ids[0].amount, 450.0)
        self.assertEquals(wizard.amount_total, 450.0)
        wizard.print_vat_intra()
