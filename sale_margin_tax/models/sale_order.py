# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.depends("order_line.tax_id")
    def _compute_has_margin_taxes(self):
        for order in self:
            order.has_margin_taxes = order._get_margin_taxes()

    def _get_margin_taxes(self):
        filter_tax = lambda t: t.amount_type == "margin"  # noqa: E731
        return self.order_line.tax_id.filtered(filter_tax)

    def _get_margin_mention(self):
        margin_tax = self._get_margin_taxes()[0]
        margin_tax = margin_tax.with_context(lang=self.partner_id.lang)
        return margin_tax.margin_mention

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.has_margin_taxes:
                msg = order._get_margin_mention()
                note = order.note or ""
                if msg not in note:
                    order.note = note + "\n" + msg
        return res
