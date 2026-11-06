# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.upgrade import util


def migrate(cr, version):
    # res.partner.company_name no longer exists in v20:
    # the commercial name can't be copied anymore
    util.remove_field(cr, "res.company", "fill_cweb_commercial_name")
    util.remove_field(cr, "res.config.settings", "fill_cweb_commercial_name")
