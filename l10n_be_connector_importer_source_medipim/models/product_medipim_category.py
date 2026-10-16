# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductMedipimCategory(models.Model):
    _name = "product.medipim.category"
    _description = "Product Medipim Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"

    name = fields.Char(
        translate=True,
        required=True,
    )
    description = fields.Char(
        translate=True,
    )
    complete_name = fields.Char(
        compute="_compute_complete_name", recursive=True, store=False
    )
    medipim_id = fields.Char(
        help="This is a technical field to represent id in Medipim database.",
        index=True,
        readonly=True,
    )
    parent_id = fields.Many2one(
        comodel_name="product.medipim.category",
        ondelete="cascade",
        index=True,
        domain="[('id', '!=', id)]",
    )
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id.complete_name")
    @api.depends_context("lang")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = (
                    f"{category.parent_id.complete_name} / {category.name}"
                )
            else:
                category.complete_name = category.name
