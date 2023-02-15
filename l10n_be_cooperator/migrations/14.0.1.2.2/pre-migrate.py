# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Delete ir_cron_mail_tax_shelter_action.")

    env = api.Environment(cr, SUPERUSER_ID, {})
    cron = env.ref("l10n_be_cooperator.ir_cron_mail_tax_shelter_action")
    data = env["ir.model.data"].search(
        [
            ("name", "=", "ir_cron_mail_tax_shelter_action"),
            ("module", "=", "l10n_be_cooperator"),
        ]
    )

    cron.unlink()
    data.unlink()
