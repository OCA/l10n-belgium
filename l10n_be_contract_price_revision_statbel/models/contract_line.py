# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):

    _inherit = "contract.line"

    def _get_first_ancestor(self):
        self.ensure_one()

        def _get_predecessor(line):
            predecessor = line
            if line.predecessor_contract_line_id:
                predecessor = _get_predecessor(line.predecessor_contract_line_id)
            return predecessor

        return _get_predecessor(self)
