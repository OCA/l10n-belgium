# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductBfciCategory(models.Model):
    _name = "product.bfci.category"
    _description = "Product Bfci Category"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "complete_name"

    name = fields.Char(
        translate=True,
    )
    complete_name = fields.Char(
        compute="_compute_complete_name", recursive=True, store=True
    )
    bfci_id = fields.Char(
        help="This is a technical field to represent id in CBIP/BFCI database.",
        index=True,
    )
    parent_id = fields.Many2one(
        comodel_name="product.bfci.category",
        ondelete="cascade",
        index=True,
        domain="[('id', '!=', id)]",
    )
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = (
                    f"{category.parent_id.complete_name} / {category.name}"
                )
            else:
                category.complete_name = category.name
