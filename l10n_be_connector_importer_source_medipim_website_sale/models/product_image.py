# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductImage(models.Model):
    _inherit = "product.image"

    medipim_id = fields.Integer(
        index=True,
    )
