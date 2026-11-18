# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Pure SQL so that it keeps working when a version is skipped (e.g. 18.0 -> 20.0)

RENAMED_PARTNER_FIELDS = [
    ("cweb_country", "cweb_country_id"),
    ("cweb_prefLang", "cweb_prefLang_id"),
]


def migrate(cr, version):
    # Rename columns (only if the old one exists and the new one doesn't)
    cr.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'res_partner' AND column_name = 'cweb_country'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'res_partner' AND column_name = 'cweb_country_id'
            ) THEN
                ALTER TABLE res_partner
                    RENAME COLUMN cweb_country TO cweb_country_id;
            END IF;
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'res_partner' AND column_name = 'cweb_prefLang'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'res_partner' AND column_name = 'cweb_prefLang_id'
            ) THEN
                ALTER TABLE res_partner
                    RENAME COLUMN "cweb_prefLang" TO "cweb_prefLang_id";
            END IF;
        END $$;
        """
    )
    # Rename field metadata
    for old, new in RENAMED_PARTNER_FIELDS:
        cr.execute(
            """
            UPDATE ir_model_fields
               SET name = %s
             WHERE model = 'res.partner' AND name = %s
               AND NOT EXISTS (
                   SELECT 1 FROM ir_model_fields
                    WHERE model = 'res.partner' AND name = %s
               )
            """,
            (new, old, new),
        )
        old_xmlid = f"field_res_partner__{old}"
        new_xmlid = f"field_res_partner__{new}"
        cr.execute(
            """
            UPDATE ir_model_data
               SET name = %s
             WHERE module = 'companyweb_base' AND name = %s
               AND NOT EXISTS (
                   SELECT 1 FROM ir_model_data
                    WHERE module = 'companyweb_base' AND name = %s
               )
            """,
            (new_xmlid, old_xmlid, new_xmlid),
        )

    # Removed fields: drop columns, field metadata (ir_model_fields) is cleaned
    # up by Odoo at the end of the upgrade, which skips missing columns
    cr.execute(
        """
        ALTER TABLE res_partner
            DROP COLUMN IF EXISTS "cweb_creditLimit_info_unset",
            DROP COLUMN IF EXISTS cweb_image_unset,
            DROP COLUMN IF EXISTS cweb_balance_year_unset,
            DROP COLUMN IF EXISTS cweb_closed_date_unset
        """
    )

    # The config parameter has a noupdate flag: switch it to the API V2.0
    cr.execute(
        """
        UPDATE ir_config_parameter
           SET value = 'https://connect.companyweb.be/V2.0/alacarteservice.asmx'
         WHERE key = 'companyweb.alacarte'
           AND value NOT LIKE '%V2.0%'
        """
    )
