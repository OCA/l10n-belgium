# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestSaleMarginTaxCase


class TestSaleMarginTax(TestSaleMarginTaxCase):
    def test_sale_invoice_tax(self):
        # when
        self.sale.action_confirm()

        # then: margin tax says 0 on SO
        self.assertEqual(self.sale.amount_tax, 0)
        # total: 4 * 25 + 1 * 15 = 115
        self.assertEqual(self.sale.amount_total, 115)
        #
        self.assertTrue("marg" in self.sale.note)

        # when
        invoice = self.sale._create_invoices()

        # then:
        # total cost: 70  = (4 * 15 + 10)
        # tax: 70 - (70 /1.21) = 12.15
        self.assertEqual(invoice.amount_tax, 12.15)
        self.assertEqual(invoice.amount_total, 115)
        self.assertTrue("marg" in invoice.narration)
