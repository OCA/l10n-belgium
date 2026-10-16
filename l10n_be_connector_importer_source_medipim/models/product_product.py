# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MedipimSourceImportRecordsetEventListener(models.Model):
    _inherit = "product.product"

    medipim_id = fields.Char(
        index=True,
        readonly=True,
    )
