# Copyright 2026 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import os

from odoo.fields import Command

from odoo.addons.connector_importer.tests.common import TestImporterBase
from odoo.addons.connector_importer_api.tests.test_connector_importer_api_common import (  # noqa
    TestConnectorImporterApiBase,
)


class ImportSourceMedipimCommon(TestImporterBase, TestConnectorImporterApiBase):
    def _get_component_modules(self):
        result = super()._get_component_modules()
        result.append("l10n_be_connector_importer_source_medipim")

        return result

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref(
            "l10n_be_connector_importer_source_medipim.import_backend_medipim"
        )
        cls.recordset = cls.env.ref(
            "l10n_be_connector_importer_source_medipim.import_recordset_medipim_product_product"
        )
        cls.recordset_category = cls.env.ref(
            "l10n_be_connector_importer_source_medipim.import_recordset_product_medipim_category"
        )
        cls.backend.debug_mode = True
        cls.source_import_api.type_request = "post"
        cls.source_import_api.stream = True
        cls.source_import_api.type_authorization = "basic_auth"
        cls.source_import_api.params_code = {"parameter 1": {"sub 1": "value 1"}}
        cls.source_import_api.username = "test"
        cls.source_import_api.password = "test"

        cls.source_import_api.write(
            {
                "header_ids": [
                    Command.create(
                        {
                            "name": "Content-Type",
                            "value": "application/json",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Accept",
                            "value": "application/x-json-stream",
                        }
                    ),
                ],
            }
        )

    def _get_image(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + "/icon.png", "rb") as f:
            image = f.read()
        return image

    def _get_photos(self):
        return [
            {
                "id": 659214,
                "type": "frontal",
                "locales": ["nl", "en"],
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
                "photoType": "packshot",
                "formats": {
                    "thumbnail": "https://dummy.png",
                    "medium": "https://dummy.png",
                    "mediumJpeg": "https://dummy.png",
                    "largePng": "https://dummy.png",
                    "large": "https://dummy.png",
                    "hugePng": "https://dummy.png",
                    "huge": "https://dummy.png",
                },
                "displayOrder": 1,
                "meta": {"createdAt": 1785941124, "updatedAt": 1786089673},
            }
        ]

    def _get_medipim_response(self, modified=False):
        return json.dumps(
            {
                "meta": {
                    "total": 1,
                },
                "result": self._get_recordset(modified=modified),
            }
        )

    def _get_medipim_category_response(self, modified=False):
        return {
            "meta": {
                "total": 2,
            },
            "result": self._get_category_recordset(modified=modified),
        }

    def _get_recordset(self, modified=False) -> list:
        # The list of Medipim values
        return [
            self._get_recordset_product_1(modified=modified),
            self._get_recordset_product_2(modified=modified),
        ]

    def _get_category_recordset(self, modified=False) -> list:
        # The list of Medipim values
        return [
            self._get_recordset_category_1(modified=modified),
            self._get_recordset_category_2(modified=modified),
        ]

    def _get_recordset_category_1(self, modified=False) -> dict:
        """
        The Medipim category 1 recordset
        """
        if modified:
            description = {
                "fr": "Description modifiée",
                "en": "Modified Description",
                "nl": "Geswijzigd beschrijving",
            }
        else:
            description = {
                "fr": "Description",
                "en": "Description",
                "nl": "Beschrijving",
            }
        return {
            "id": "M0000000001",
            "name": {"fr": "Category 1", "en": "Category 1", "nl": "Category 1"},
            "description": description,
        }

    def _get_recordset_category_2(self, modified=False) -> dict:
        """
        The Medipim category 2 recordset
        """
        if modified:
            description = {
                "fr": "Description modifiée",
                "en": "Modified Description",
                "nl": "Geswijzigd beschrijving",
            }
        else:
            description = {
                "fr": "Description 2",
                "en": "Description 2",
                "nl": "Beschrijving 2",
            }
        return {
            "id": "M0000000002",
            "name": {"fr": "Category 2", "en": "Category 2", "nl": "Category 2"},
            "description": description,
        }

    def _get_recordset_product_1(self, modified=False) -> dict:
        """
        The Medipim product 1 recordset
        """
        if modified:
            weight = {"value": 200, "unit": "g"}
        else:
            weight = {"value": 100, "unit": "g"}
        return {
            "id": "M0000000001",
            "status": "active",
            "name": {"fr": "Produit 1", "en": "Product 1", "nl": "Produkt 1"},
            "cnk": "12348798",
            "ean": ["1234567891012"],
            "weightWithUnit": weight,
            "frontals": self._get_photos(),
            "medipimCategories": [
                {
                    "id": "M0000000001",
                    "name": {
                        "nl": "Category 1",
                        "fr": "Category 1",
                        "en": "null",
                        "de": "null",
                    },
                    "parent": "null",
                    "order": 1,
                }
            ],
        }

    def _get_recordset_product_2(self, modified=False) -> dict:
        """
        The Medipim product 1 recordset
        """
        if modified:
            weight = {"value": 160, "unit": "g"}
        else:
            weight = {"value": 150, "unit": "g"}
        return {
            "id": "M0000000002",
            "status": "replaced",
            "name": {"fr": "Produit 2", "en": "Product 2", "nl": "Produkt 2"},
            "cnk": "12348799",
            "ean": ["1234567891013"],
            "weightWithUnit": weight,
        }

    def _get_product_1_values(self) -> dict:
        # The product Odoo record values
        tags = self.env["product.tag"].search([("is_medipim", "=", True)])
        return {
            "barcode": "1234567891012",
            "weight": 0.1,
            "medipim_id": "M0000000001",
            "name": "Product 1",
            "active": True,
            "state": "sellable",
            "cnk_code": "12348798",
            "product_tag_ids": tags.ids,
        }

    def _get_product_2_values(self) -> dict:
        # The product Odoo record values
        return {
            "barcode": "1234567891013",
            "weight": 0.15,
            "medipim_id": "M0000000002",
            "name": "Product 2",
            "active": True,
            "state": "obsolete",
            "cnk_code": "12348799",
            "product_tag_ids": [],
        }

    def _get_category_1_values(self) -> dict:
        # The category Odoo record values
        return {
            "medipim_id": "M0000000001",
            "name": "Category 1",
            "description": "Description",
        }

    def _get_category_2_values(self) -> dict:
        # The category Odoo record values
        return {
            "medipim_id": "M0000000002",
            "name": "Category 2",
            "description": "Description 2",
        }

    def _get_recordset_values(self):
        return [self._get_product_1_values(), self._get_product_2_values()]

    def _get_recordset_categories_values(self):
        return [self._get_category_1_values(), self._get_category_2_values()]

    def _get_products(self):
        return self.env["product.product"].with_context(active_test=False).search([])

    def _get_categories(self):
        return (
            self.env["product.medipim.category"]
            .with_context(active_test=False)
            .search([])
        )

    def _create_category(self):
        self.category = self.env["product.medipim.category"].create(
            {"medipim_id": "M0000000001", "name": "Category 1"}
        )
