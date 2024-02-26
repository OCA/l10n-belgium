# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models

mention = (
    "Livraison soumise au régime particulier d'imposition "
    "de la marge bénéficiaire. TVA non déductible."
)


class AccountMove(models.Model):
    _inherit = "account.move"

    has_margin_taxes = fields.Boolean(compute="_compute_has_margin_taxes")

    @api.depends("line_ids.tax_ids")
    def _compute_has_margin_taxes(self):
        for move in self:
            move.has_margin_taxes = any(move.mapped("line_ids.has_margin_taxes"))

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.has_margin_taxes:
                msg = _(mention)
                narration = move.narration or ""
                if msg not in narration:
                    move.narration = narration + "<br/>" + msg
        return res
