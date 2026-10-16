# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class MedipimProductMedipimCategoryRecordHandler(Component):
    """Interact w/ odoo importable records."""

    _name = "product.medipim.category.handler"
    _inherit = "importer.odoorecord.handler"
    _apply_on = "product.medipim.category"
    _usage = "medipim.record"

    def odoo_post_create(self, odoo_record, values, orig_values):
        self._update_parents(odoo_record, values, orig_values)

    def _update_parents(self, odoo_record, values, orig_values):
        """
        State is on product template side
        """
        if "parent" in orig_values:
            parent_id = orig_values.get("parent")
            category = self.env["product.medipim.category"].search(
                [("medipim_id", "=", parent_id)]
            )
            if category:
                odoo_record.parent_id = category


# class ProductProductRecordHandler(Component):
#     """Interact w/ odoo importable records."""

#     _name = "product.product.handler"
#     _inherit = "importer.odoorecord.handler"
#     _apply_on = "product.product"
