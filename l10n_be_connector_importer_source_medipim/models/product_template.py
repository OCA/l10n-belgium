# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    medipim_category_ids = fields.Many2many(
        relation="product_template_medipim_category_rel",
        column1="product_tmpl_id",
        column2="medipim_category_id",
        comodel_name="product.medipim.category",
        index=True,
    )
