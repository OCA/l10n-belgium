# Copyright 2026 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from markupsafe import Markup

from odoo.addons.l10n_be_connector_importer_source_medipim.tests.common import (  # noqa
    ImportSourceMedipimCommon,
)


class ImportSourceMedipimDescriptionCommon(ImportSourceMedipimCommon):
    def _get_component_modules(self):
        result = super()._get_component_modules()
        result.append("l10n_be_connector_importer_source_medipim_description")
        return result

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _get_recordset_product_1(self, modified=False) -> dict:
        """
        The Medipim product 1 recordset
        """
        result = super()._get_recordset_product_1(modified=modified)
        result["descriptions"] = [
            {
                "id": 1000000,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "contra_indication",
                "content": {
                    "nl": "<p><em>Contra indication.</em></p>\n",
                    "fr": "<div>\n<p><em>Contre indication.</em></p>\n</div>\n",
                    "en": False,
                    "de": False,
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785499549, "updatedAt": 1785499549},
            },
            {
                "id": 1000001,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "properties",
                "content": {
                    "nl": "<ul>\n<li><span>Property 1</span></li>\n<li><span>Property 2</span></li>\n</ul>\n",  # noqa
                    "fr": "<ul>\n<li><span>Property 1</span></li>\n<li><span>Property 2</span></li>\n</ul>\n",  # noqa
                    "en": "<ul>\n<li><span>Property 1</span></li>\n<li><span>Property 2</span></li>\n</ul>\n",  # noqa
                    "de": "<ul>\n<li><span>Property 1</span></li>\n<li><span>Property 2</span></li>\n</ul>\n",  # noqa
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785499608, "updatedAt": 1785499608},
            },
            {
                "id": 1006448,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "composition",
                "content": {
                    "nl": "<p>Composition</p>\n",
                    "fr": "<div>Composition</div>",
                    "en": "null",
                    "de": "null",
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785499665, "updatedAt": 1785499665},
            },
            {
                "id": 1000002,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "full_description",
                "content": {
                    "nl": "<p>Full Description</p>",
                    "fr": "<p>Full Description</p>",
                    "en": False,
                    "de": False,
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785499701, "updatedAt": 1785499865},
            },
            {
                "id": 1006450,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "indication",
                "content": {
                    "nl": "<p>Indication</p>\n",
                    "fr": "<div>\n<p>Indication</p>\n</div>\n",
                    "en": False,
                    "de": False,
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785499972, "updatedAt": 1785501396},
            },
            {
                "id": 1000006,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "nutritional_value",
                "content": {
                    "nl": "<p>Compo</p>",
                    "fr": "<p>Compo</p>",
                    "en": False,
                    "de": False,
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785500145, "updatedAt": 1785500145},
            },
            {
                "id": 100004,
                "locales": ["nl", "fr"],
                "targetGroups": [
                    "public",
                    "pharmacist",
                    "doctor",
                    "homecare",
                    "hospital",
                    "nurse",
                    "physiotherapist",
                    "webshop",
                ],
                "type": "usage",
                "content": {
                    "nl": "<p>Usage</p>\n",
                    "fr": "<p>Usage</p>",
                    "en": "<p>Usage</p>",
                    "de": False,
                },
                "descriptionTag": "user_generated",
                "meta": {"createdAt": 1785505502, "updatedAt": 1785505502},
            },
            {
                "id": 1000002,
                "locales": ["nl", "fr", "en", "de"],
                "targetGroups": ["public"],
                "type": "legal_text",
                "content": {
                    "nl": "<p>Legal Text</p>",
                    "fr": "<p>Legal Text</p>",
                    "en": "<p>Legal Text</p>",
                    "de": "<p>Legal Text</p>",
                },
                "descriptionTag": "system_generated",
                "meta": {"createdAt": 1785535239, "updatedAt": 1785535239},
            },
        ]

        return result

    def _get_product_1_values(self) -> dict:
        # The product Odoo record values
        values = super()._get_product_1_values()
        values["medical_usage"] = Markup("<p>Usage</p>")
        values["medical_contra_indication"] = Markup(
            "<div>\n<p><em>Contre indication.</em></p>\n</div>\n"
        )
        return values

    def _get_product_2_values(self) -> dict:
        # The product Odoo record values
        values = super()._get_product_2_values()
        values["medical_usage"] = False
        values["medical_contra_indication"] = False
        return values
