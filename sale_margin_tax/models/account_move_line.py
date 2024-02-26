# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")
    price_subtotal_report = fields.Monetary(
        string="Subtotal (Report)",
        compute="_compute_price_subtotal_report",
        currency_field="currency_id",
    )

    @api.depends("tax_ids")
    def _compute_has_margin_taxes(self):
        mg = self.env.ref("sale_margin_tax.tax_group_margin")
        for line in self:
            line.has_margin_taxes = mg in line.mapped("tax_ids.tax_group_id")

    @api.depends("price_subtotal", "price_total", "has_margin_taxes")
    def _compute_price_subtotal_report(self):
        for line in self:
            price = line.price_total if line.has_margin_taxes else line.price_subtotal
            line.price_subtotal_report = price
