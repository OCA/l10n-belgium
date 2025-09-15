# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    soda_auto_map = fields.Boolean(
        string="SODA Auto Map",
        related="company_id.soda_auto_map",
        readonly=False,
        help="Enable automatic mapping of SODA import data",
    )
