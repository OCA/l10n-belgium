# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import date

from lxml.etree import XML

from .common import TestVatReportsCommon


class TestVatListing(TestVatReportsCommon):
    def setUp(self):
        super(TestVatReportsCommon, self).setUp()
        company = self.env.user.company_id
        tax = self.env.ref("l10n_be.%s_attn_VAT-OUT-21-S" % company.id)
        self._create_test_data(tax)

    def _prepare_listing(self):
        year = date.today().year
        wizard = self.env["partner.vat"].create(
            {"year": str(year), "limit_amount": 1}
        )
        action = wizard.get_partners()
        vat_list_id = action["res_id"]
        vat_list = self.env["partner.vat.list"].browse(vat_list_id)

        self.assertEqual(94.5, vat_list.total_vat)
        return vat_list

    def test_xml_list(self):
        full_list = self._prepare_listing()
        full_list.create_xml()
        ns = {"ns2": "http://www.minfin.fgov.be/ClientListingConsignment"}
        xml = XML(base64.b64decode(full_list.file_save))
        xml_vat_amount = xml.xpath(
            '//ns2:Client[ns2:CompanyVATNumber[text() = "0477472701"]]'
            "/ns2:VATAmount",
            namespaces=ns,
        )[0].text
        self.assertEqual("94.50", xml_vat_amount)

    def test_pdf_list(self):
        full_list = self._prepare_listing()
        full_list.print_vatlist()
