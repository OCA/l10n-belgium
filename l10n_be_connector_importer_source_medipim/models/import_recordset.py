# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ImportRecordset(models.Model):
    _inherit = "import.recordset"

    last_run_on_timestamp = fields.Integer(
        compute="_compute_last_run_on_timestamp",
    )

    @api.depends("last_run_on")
    def _compute_last_run_on_timestamp(self):
        for record in self:
            record.last_run_on_timestamp = record.last_run_on.timestamp()
