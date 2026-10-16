# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ProductMedipimCategoryMapper(Component):
    _name = "product.medipim.category.medipim.mapper"
    _inherit = "importer.base.mapper"
    _apply_on = "product.medipim.category"

    direct = [  # noqa
        ("id", "medipim_id"),
        ("name", "name"),
        ("description", "description"),
    ]
    required = {  # noqa
        "name": "name",
        "id": "medipim_id",
    }
    translatable = ["name", "description"]  # noqa

    @mapping
    def parent(self, record):
        result = {}
        if "parent" in record and record["parent"] is None:
            result["parent_id"] = False
        return result
