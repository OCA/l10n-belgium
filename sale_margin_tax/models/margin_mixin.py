# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class MarginLineMixin(models.AbstractModel):
    _name = "margin.line.mixin"
    _description = "Margin Line Mixin"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.model
    def _get_tax_field(self):
        return "tax_id" if self._name == "sale.order.line" else "tax_ids"

    @api.model
    def _get_margin_depends(self):
        tax_field = self._get_tax_field()
        return [tax_field + ".is_margin_tax"]

    def _get_line_taxes(self):
        tax_field = self._get_tax_field()
        return self[tax_field]

    def _get_margin_taxes(self):
        taxes = self._get_line_taxes()
        return taxes.filtered("is_margin_tax")

    @api.depends(lambda self: self._get_margin_depends())
    def _compute_has_margin_taxes(self):
        for line in self:
            line.has_margin_taxes = line._get_margin_taxes()


class MarginMixin(models.AbstractModel):
    _name = "margin.mixin"
    _description = "Margin Mixin"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.model
    def _get_margin_depends(self):
        line_field = self._get_lines_field()
        return [line_field + ".has_margin_taxes"]

    def _get_lines_field(self):
        return "order_line" if self._name == "sale.order" else "line_ids"

    def _get_lines(self):
        line_field = self._get_lines_field()
        return self[line_field]

    @api.depends(lambda self: self._get_margin_depends())
    def _compute_has_margin_taxes(self):
        for record in self:
            lines = record._get_lines()
            record.has_margin_taxes = any(lines.mapped("has_margin_taxes"))

    def _get_margin_taxes(self):
        lines = self._get_lines()
        return lines._get_margin_taxes()

    def _get_margin_mention(self):
        margin_tax = self._get_margin_taxes()[0]
        margin_tax = margin_tax.with_context(lang=self.partner_id.lang)
        return margin_tax.margin_mention
