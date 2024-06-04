# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "margin.line.mixin"]

    price_subtotal_report = fields.Monetary(
        string="Subtotal (Report)",
        compute="_compute_price_subtotal_report",
        currency_field="currency_id",
    )
    price_unit_report = fields.Monetary(
        string="Price Unit (Report)",
        compute="_compute_price_subtotal_report",
        currency_field="currency_id",
    )
    is_margin_line = fields.Boolean(
        help="True if this line is a margin line.",
        default=False,
    )
    margin_line_id = fields.Many2one(
        "account.move.line",
        help="The margin line for this line.",
    )

    @api.depends("price_subtotal", "price_total", "has_margin_taxes")
    def _compute_price_subtotal_report(self):
        for line in self:
            price = line.price_subtotal
            price_unit = line.price_unit
            if line.has_margin_taxes:
                price = line.price_total + line.margin_line_id.price_total
                price_unit = price_unit + line.margin_line_id.price_unit
            line.price_subtotal_report = price
            line.price_unit_report = price_unit
