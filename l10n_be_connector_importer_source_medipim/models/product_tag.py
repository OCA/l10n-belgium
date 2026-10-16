# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTag(models.Model):
    _inherit = "product.tag"

    is_medipim = fields.Boolean()
