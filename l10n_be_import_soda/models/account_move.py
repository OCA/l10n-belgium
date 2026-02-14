# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    soda_ref = fields.Char(string="SODA Reference", readonly=True)

    def _get_edi_decoder(self, file_data, new=False):
        if self.journal_id.import_soda and self.journal_id._is_soda_file(
            file_data["attachment"]
        ):
            return self._soda_edi_decoder
        return super()._get_edi_decoder(file_data, new=new)

    def _soda_edi_decoder(self, move, file_data, new=False):
        return move.journal_id._import_soda_file(file_data["attachment"], move=move)
