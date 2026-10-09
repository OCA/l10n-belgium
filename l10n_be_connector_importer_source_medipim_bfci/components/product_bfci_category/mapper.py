# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def first_ean(record):
    return record[:1]


class ProductBfciCategoryMapper(Component):
    _name = "product.bfci.category.medipim.mapper"
    _inherit = "importer.base.mapper"
    _apply_on = "product.bfci.category"

    direct = [  # noqa
        ("id", "bfci_id"),
        ("name", "name"),
    ]
    required = {  # noqa
        "name": "name",
        "id": "bfci_id",
    }
    translatable = ["name"]  # noqa

    @mapping
    def parent(self, record):
        result = {}
        if "parent" in record and record["parent"] is None:
            result["parent_id"] = False
        return result
