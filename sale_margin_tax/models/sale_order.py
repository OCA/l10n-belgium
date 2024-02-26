# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

mention = (
    "Livraison soumise au régime particulier d'imposition "
    "de la marge bénéficiaire. TVA non déductible."
)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.depends("order_line.tax_id")
    def _compute_has_margin_taxes(self):
        for order in self:
            order.has_margin_taxes = "margin" in order.mapped(
                "order_line.tax_id.amount_type"
            )

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.has_margin_taxes:
                msg = _(mention)
                note = order.note or ""
                if msg not in note:
                    order.note = note + "\n" + msg
        return res
