# Copyright 2026 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from io import StringIO
from unittest.mock import patch

import requests
from requests import Response

from odoo.addons.l10n_be_connector_importer_source_medipim.components.product_product.mapper import (  # noqa
    ProductProductMapper,
)
from odoo.addons.l10n_be_connector_importer_source_medipim.tests.common import (
    ImportSourceMedipimCommon,
)


class TestSourceApiPost(ImportSourceMedipimCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def _get_recordset_product_1(self, modified=False) -> dict:
        result = super()._get_recordset_product_1(modified=modified)
        result.update(
            {
                "photos": self._get_photos(),
            }
        )
        return result

    def _get_product_1_values(self) -> dict:
        result = super()._get_product_1_values()
        result["product_variant_image_ids"] = self.products[
            0
        ].product_variant_image_ids.ids
        return result

    def _get_product_2_values(self) -> dict:
        result = super()._get_product_2_values()
        result["product_variant_image_ids"] = []
        return result

    def test_import(self):
        self.product_before = self._get_products()
        with patch.object(requests, "post") as mock_post:
            response = Response()
            response.status_code = 200
            m_response = self._get_medipim_response()
            response.raw = StringIO(str(m_response))
            mock_post.return_value = response
            with patch.object(ProductProductMapper, "_get_image_content") as mock_image:
                mock_image.return_value = self._get_image()
                self.recordset.run_import()

        self.products = self._get_products() - self.product_before

        self.assertEqual(2, len(self.products))

        self.assertRecordValues(
            self.products,
            self._get_recordset_values(),
        )
