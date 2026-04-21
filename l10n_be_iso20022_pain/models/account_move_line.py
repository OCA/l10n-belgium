# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_communication(self):
        self.ensure_one()
        communication_type, communication = super()._get_communication()
        if self.move_id.reference_type == "structured":
            communication = communication.replace("+", "").replace("/", "")
        return communication_type, communication
