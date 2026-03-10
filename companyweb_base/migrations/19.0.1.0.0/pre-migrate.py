# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.partner", "cweb_country", "cweb_country_id")
    util.rename_field(cr, "res.partner", "cweb_prefLang", "cweb_prefLang_id")

    util.remove_field(cr, "res.partner", "cweb_creditLimit_info_unset")
    util.remove_field(cr, "res.partner", "cweb_image_unset")
    util.remove_field(cr, "res.partner", "cweb_balance_year_unset")
    util.remove_field(cr, "res.partner", "cweb_closed_date_unset")

    # Force update config parameter that has a noupdate flag
    util.update_record_from_xml(cr, "companyweb_base.companyweb_alacarte")
