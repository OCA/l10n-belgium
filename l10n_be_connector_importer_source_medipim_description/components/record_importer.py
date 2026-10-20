# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component

from ..utils import _get_product_description_mapping


class MedipimRecordImporter(Component):
    _inherit = "medipim.importer.record"

    def _get_description_fields(self, result_line):
        """
        Get each description key to field

        As the same description type can be spread in several keys like:

        "descriptions": [
            {
                "id": "id",
                "type": "usage",
                "locales": ["fr", "nl"],
                "content": {
                    "nl": "nl",
                    "fr": "fr",
                    "en": False,
                    "de": False,
                }
            },
            {
                "id": "id",
                "type": "usage",
                "locales": ["en"],
                "content": {
                    "nl": "False,
                    "fr": False,
                    "en": "en",
                    "de": False,
                }
            },
        ]

        We should rebuild the field with different languages collection
        in a new dict like

        {
            "field": {
                "nl": "nl",
                "fr": "fr",
                "en": "en",
            }
        }
        """
        descriptions = result_line.get("descriptions")
        if descriptions:
            mapping = _get_product_description_mapping()
            for description in descriptions:
                field_type = description.get("type")
                if field_type in mapping:
                    localized_description = {}
                    for locale in description.get("locales"):
                        localized_description[locale] = description.get("content").get(
                            locale
                        )
                    field_mapping = mapping.get(field_type)
                    if field_mapping in result_line:
                        for locale, value in localized_description.items():
                            result_line[field_mapping][locale] = value
                    else:
                        result_line[field_mapping] = {}
                        for locale, value in localized_description.items():
                            result_line[field_mapping][locale] = value
        return result_line

    def _get_translations(self, result_line):
        # Be sure to be just before keys translations
        result = self._get_description_fields(result_line)
        return super()._get_translations(result)
