# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component

from ...utils import _get_product_description_mapping


class ProductProductMapper(Component):
    _inherit = "product.product.medipim.mapper"

    def __init__(self, work_context):
        super().__init__(work_context)
        # Extend the direct mapping and the translatable keys
        direct = [
            (element, element)
            for element in _get_product_description_mapping().values()
        ]
        self.direct.extend(direct)
        self.translatable.extend(list(_get_product_description_mapping().values()))
