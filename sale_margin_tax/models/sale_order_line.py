# Copyright 2020 ACSONE SA/NV
# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "margin.line.mixin"]

    def _get_taxes(self):
        """Override to get the purchase price from lot, purchase order, etc.
        The default simply returns the tax from the line itself
        """
        return self.tax_id

    def _get_purchase_price(self):
        """Override to get the purchase price from lot, purchase order, etc.
        The default simply returns the standard price of the product.
        """
        return self.product_id.standard_price * self.product_uom_qty

    def _get_margin(self):
        purchase_price = self._get_purchase_price()
        return max(self.price_subtotal - purchase_price, 0)

    def _get_margin_base_price(self):
        base_price = self.price_subtotal
        margin = self._get_margin()
        return base_price - margin

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        taxes = self._get_taxes()
        if "margin" in taxes.mapped("amount_type"):
            vals["is_margin_line"] = True
            qty = self.product_uom_qty
            product = self.env.ref("sale_margin_tax.product_margin")
            vals["product_id"] = product.id
            margin = self._get_margin()
            taxes = taxes._apply_margin_taxes(margin, 0)
            vals["price_unit"] = margin / qty
            vals["tax_ids"] = [(6, 0, taxes.ids)] if taxes else [(5, 0, 0)]
        return vals

    def _prepare_invoice_margin_base_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        taxes = self._get_taxes()
        tax_null = taxes.margin_base_tax_id
        qty = self.product_uom_qty
        base_values = {
            "price_unit": self._get_margin_base_price() / qty,
            "quantity": qty,
            "tax_ids": [(6, 0, tax_null.ids)],
        }
        vals.update(base_values)
        return vals
