# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Pure SQL so that it keeps working when a version is skipped


def migrate(cr, version):
    # res.partner.company_name no longer exists in v20:
    # the commercial name can't be copied anymore.
    # Field metadata (ir_model_fields) is cleaned up by Odoo at the end of the
    # upgrade, which skips missing columns
    cr.execute(
        "ALTER TABLE res_company DROP COLUMN IF EXISTS fill_cweb_commercial_name"
    )
    cr.execute(
        "ALTER TABLE res_config_settings "
        "DROP COLUMN IF EXISTS fill_cweb_commercial_name"
    )
