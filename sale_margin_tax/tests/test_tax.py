# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestSaleMarginTaxCase


class TestSaleMarginTax(TestSaleMarginTaxCase):
    def test_sale_invoice_tax(self):
        """Sell two products with margin tax"""
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

    def test_mixed_taxes(self):
        """First line has normal tax, other is on margin"""
        # given:
        self.sale.order_line[0].tax_id = self.tax_other

        # when
        self.sale.action_confirm()

        # then: tax is properly applied for the first line
        self.assertEqual(self.sale.amount_tax, 21)
        # total: 4 * 25 + 21 + 1 * 15 = 115
        self.assertEqual(self.sale.amount_total, 136)
        self.assertTrue("marg" in self.sale.note)

        # when
        invoice = self.sale._create_invoices()

        # then:
        # total cost on margin: 5, sold for 15
        # margin tax: 10 - (10 /1.21) = 1.74
        # plus the 21% on 100€ for the other line
        self.assertAlmostEqual(invoice.amount_tax, 22.74, 2)
        self.assertEqual(invoice.amount_total, 136)
        self.assertTrue("marg" in invoice.narration)

    def test_no_margin_tax(self):
        """Sell one product with normal tax; nothing fancy should happen."""
        # given
        self.sale.order_line[0].tax_id = self.tax_other
        self.sale.order_line[1].unlink()

        # when
        self.sale.action_confirm()

        # then: tax is properly applied
        self.assertEqual(self.sale.amount_tax, 21)
        self.assertEqual(self.sale.amount_total, 121)
        self.assertFalse("marg" in (self.sale.note or ""))

        # when
        invoice = self.sale._create_invoices()

        # then:
        self.assertEqual(invoice.amount_tax, 21)
        self.assertEqual(invoice.amount_total, 121)
        self.assertFalse("marg" in (invoice.narration or ""))

    def test_french_translation(self):
        """Everything should work in French."""
        # given
        fr_description = "Marge svp"
        translation = {"fr_BE": fr_description}
        self.tax_margin.update_field_translations("margin_mention", translation)
        self.partner.lang = "fr_BE"

        # when
        self.sale.action_confirm()

        # then: same as before, but in French
        self.assertEqual(self.sale.amount_tax, 0)
        self.assertEqual(self.sale.amount_total, 115)
        self.assertTrue("svp" in (self.sale.note or ""))

        # when
        invoice = self.sale._create_invoices()

        # then:
        self.assertEqual(invoice.amount_tax, 12.15)
        self.assertEqual(invoice.amount_total, 115)
        self.assertTrue("svp" in (invoice.narration or ""))
