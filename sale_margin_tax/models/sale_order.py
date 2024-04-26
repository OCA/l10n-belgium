# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "margin.mixin"]

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.has_margin_taxes:
                msg = order._get_margin_mention()
                note = order.note or ""
                if msg not in note:
                    order.note = note + "\n" + msg
        return res

    def _create_invoices(self, grouped=False, final=False):
        res = super()._create_invoices(grouped=grouped, final=final)
        for invoice in res:
            if self.has_margin_taxes:
                for line in self.order_line.filtered("has_margin_taxes"):
                    invoice_line = line.invoice_lines  # will crash in many cases...
                    vals_line = line._prepare_invoice_margin_base_line()
                    vals_line["move_id"] = invoice.id
                    vals_line["margin_line_id"] = invoice_line.id
                    self.env["account.move.line"].create(vals_line)
        return res
