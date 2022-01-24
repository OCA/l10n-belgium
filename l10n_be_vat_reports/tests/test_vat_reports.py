# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import TestVatReportsCommon


class TestVatListing(TestVatReportsCommon):
    def setUp(self):
        super(TestVatReportsCommon, self).setUp()
        company = self.env.user.company_id
        tax = self.env.ref("l10n_be.%s_attn_VAT-OUT-21-S" % company.id)
        self._create_test_data(tax)

    def test_partner_vat_listing(self):
        year = fields.Date.today().year
        partner_vat_list = self.env["partner.vat.list"].create(
            {"year": year, "limit_amount": 1}
        )
        partner_vat_list.get_partners()

        self.assertEquals(partner_vat_list.total_turnover, 450.)
        self.assertEqual(partner_vat_list.total_vat, 94.5)

        # coverage
        partner_vat_list.create_xml()
        partner_vat_list.print_vatlist()
