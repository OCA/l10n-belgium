# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    soda_mapping = fields.Char(
        help="SODA account mapping, multiple mappings are separated by a comma"
    )

    # TODO: constraint to enforce deterministic mapping?
