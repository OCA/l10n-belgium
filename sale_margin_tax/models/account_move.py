# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.depends("line_ids.tax_ids")
    def _compute_has_margin_taxes(self):
        for move in self:
            move.has_margin_taxes = any(move.mapped("line_ids.has_margin_taxes"))

    def _get_margin_taxes(self):
        filter_tax = lambda t: t.amount_type == "margin"  # noqa: E731
        return self.line_ids.tax_ids.filtered(filter_tax)

    def _get_margin_mention(self):
        margin_tax = self._get_margin_taxes()[0]
        margin_tax = margin_tax.with_context(lang=self.partner_id.lang)
        return margin_tax.margin_mention

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.has_margin_taxes:
                msg = move._get_margin_mention()
                narration = move.narration or ""
                if msg not in narration:
                    move.narration = narration + "<br/>" + msg
        return res
