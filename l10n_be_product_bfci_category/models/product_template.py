# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bfci_category_id = fields.Many2one(
        comodel_name="product.bfci.category",
        index=True,
    )
