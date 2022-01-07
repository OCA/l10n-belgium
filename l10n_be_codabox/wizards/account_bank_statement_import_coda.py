# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountBankStatementImportCoda(models.TransientModel):
    _inherit = "account.bank.statement.import"
    _description = (
        "Codabox Import Bank Statement, change attachment_ids to"
        "required = False, and allow to add attachment via a method"
    )

    attachment_ids = fields.Many2many(required=False)

    def attach_coda_file(self, coda_entry):
        """
        Creates and adds the coda file from the coda_entry into attachment_ids
        :param coda_entry: a codabox entry that has a file.
        :return: None
        """
        self.ensure_one()

        self.attachment_ids = [
            (
                4,
                self.env["ir.attachment"]
                .create(
                    {
                        "name": coda_entry.coda_filename,
                        "res_id": self.id,
                        "res_model": "account.bank.statement.import",
                        "datas": coda_entry.coda_file,
                        "type": "binary",
                    }
                )
                .id,
                0,
            )
        ]
