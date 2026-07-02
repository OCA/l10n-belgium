# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    companyweb_payment_info_enable = fields.Boolean(
        "Send Open Invoices to Companyweb",
        default=True,
    )
