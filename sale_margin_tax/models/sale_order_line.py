# Copyright 2020 ACSONE SA/NV
# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        taxes = self._get_taxes()
        if "margin" in taxes.mapped("amount_type"):
            purchase_price = self._get_purchase_price()
            taxes = taxes._apply_margin_taxes(self.price_subtotal, purchase_price)
        if taxes:
            vals["tax_ids"] = [(6, 0, taxes.ids)]
        else:
            vals.pop("tax_ids", False)
        return vals
