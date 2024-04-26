# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "margin.mixin"]

    invoice_report_line_ids = fields.One2many(
        "account.move.line",
        "move_id",
        string="Invoice Report lines",
        copy=False,
        readonly=True,
        domain=[
            ("display_type", "in", ("product", "line_section", "line_note")),
            ("is_margin_line", "=", False),
        ],
    )

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.has_margin_taxes:
                msg = move._get_margin_mention()
                narration = move.narration or ""
                if msg not in narration:
                    move.narration = narration + "<br/>" + msg
        return res
