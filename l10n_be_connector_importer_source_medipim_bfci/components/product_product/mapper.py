# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def first_ean(record):
    return record[:1]


class ProductProductMapper(Component):
    _inherit = "product.product.medipim.mapper"

    @mapping
    def bfciCategory(self, record):
        result = {}
        categ_id = record.get("bcfiCategory")
        if categ_id:
            category = self.env["product.bfci.category"].search(
                [("bfci_id", "=", categ_id.get("id"))], limit=1
            )
            result["bfci_category_id"] = category.id
        return result
