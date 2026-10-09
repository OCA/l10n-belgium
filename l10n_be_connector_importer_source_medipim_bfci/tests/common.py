# Copyright 2026 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.l10n_be_connector_importer_source_medipim.tests.common import (
    ImportSourceMedipimCommon,
)


class ImportSourceMedipimBfciCommon(ImportSourceMedipimCommon):
    def _get_component_modules(self):
        result = super()._get_component_modules()
        result.append("l10n_be_connector_importer_source_medipim_bfci")

        return result

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.recordset_bfci_category = cls.env.ref(
            "l10n_be_connector_importer_source_medipim_bfci.import_recordset_medipim_bfci_category"
        )

    def _get_medipim_bfci_category_response(self, modified=False):
        return {
            "meta": {
                "total": 3,
            },
            "result": self._get_bfci_category_recordset(modified=modified),
        }

    def _get_bfci_category_recordset(self, modified=False) -> list:
        # The list of Medipim values
        return [
            self._get_bfci_recordset_category_1(modified=modified),
            self._get_bfci_recordset_category_2(modified=modified),
            self._get_bfci_recordset_category_3(modified=modified),
        ]

    def _get_bfci_recordset_category_1(self, modified=False) -> dict:
        """
        The Medipim category 1 recordset
        """
        return {
            "id": "000000001",
            "name": {"fr": "Category 1", "en": "Category 1", "nl": "Category 1"},
        }

    def _get_bfci_recordset_category_2(self, modified=False) -> dict:
        """
        The Medipim category 2 recordset
        """
        return {
            "id": "000000002",
            "name": {"fr": "Category 2", "en": "Category 2", "nl": "Category 2"},
        }

    def _get_bfci_recordset_category_3(self, modified=False) -> dict:
        """
        The Medipim category 3 recordset
        """
        return {
            "id": "000000003",
            "name": {"fr": "Category 3", "en": "Category 3", "nl": "Category 3"},
            "parent": "000000002",
        }

    def _get_recordset_product_1(self, modified=False) -> dict:
        """
        The Medipim product 1 recordset
        """
        result = super()._get_recordset_product_1(modified=modified)

        result["bcfiCategory"] = {
            "id": "000000001",
            "name": {
                "nl": "Category 1",
                "fr": "Category 1",
                "en": "null",
                "de": "null",
            },
            "parent": "null",
            "order": 1,
        }

        return result

    def _get_recordset_product_2(self, modified=False) -> dict:
        """
        The Medipim product 1 recordset
        """
        result = super()._get_recordset_product_2(modified=modified)
        if modified:
            result["bcfiCategory"] = {
                "id": "000000002",
                "name": {
                    "nl": "Category 2",
                    "fr": "Category 2",
                    "en": "null",
                    "de": "null",
                },
                "parent": "null",
                "order": 2,
            }

        return result

    def _get_bfci_category_1_values(self) -> dict:
        # The category Odoo record values
        return {
            "bfci_id": "000000001",
            "name": "Category 1",
        }

    def _get_bfci_category_2_values(self) -> dict:
        # The category Odoo record values
        return {
            "bfci_id": "000000002",
            "name": "Category 2",
        }

    def _get_bfci_category_3_values(self) -> dict:
        # The category Odoo record values
        return {
            "bfci_id": "000000003",
            "name": "Category 3",
        }

    def _get_recordset_bfci_categories_values(self):
        return [
            self._get_bfci_category_1_values(),
            self._get_bfci_category_2_values(),
            self._get_bfci_category_3_values(),
        ]

    def _get_bfci_categories(self):
        return (
            self.env["product.bfci.category"].with_context(active_test=False).search([])
        )

    def _create_bfci_category(self):
        self.bfci_category = self.env["product.bfci.category"].create(
            {"bfci_id": "000000001", "name": "Category 1"}
        )
