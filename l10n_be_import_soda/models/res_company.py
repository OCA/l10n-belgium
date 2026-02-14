# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    soda_auto_map = fields.Boolean(
        string="SODA Auto Map",
        default=False,
        help="Enable automatic mapping of SODA import data",
    )
