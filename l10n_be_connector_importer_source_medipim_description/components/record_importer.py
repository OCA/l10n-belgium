# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component

from ..utils import _get_product_description_mapping


class MedipimRecordImporter(Component):
    _inherit = "medipim.importer.record"

    def _get_description_fields(self, result_line):
        """
        Get each description key to field
        """
        descriptions = result_line.get("descriptions")
        if descriptions:
            mapping = _get_product_description_mapping()
            for description in descriptions:
                field_type = description.get("type")
                if field_type in mapping:
                    result_line[mapping.get(field_type)] = description.get("content")
        return result_line

    def _get_translations(self, result_line):
        # Be sure to be just before keys translations
        result = self._get_description_fields(result_line)
        return super()._get_translations(result)
