# Copyright 2026 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from io import StringIO
from unittest.mock import patch

import requests
from requests import Response

from odoo.addons.l10n_be_connector_importer_source_medipim.components.product_product.mapper import (  # noqa
    ProductProductMapper,
)

from .common import ImportSourceMedipimDescriptionCommon


class TestSourceDescriptionApiPost(ImportSourceMedipimDescriptionCommon):
    def test_import(self):
        self._create_category()
        self.categories_before = self._get_categories()
        self.product_before = self._get_products()
        with patch.object(requests, "post") as mock_post:
            response = Response()
            response.status_code = 200
            response.raw = StringIO(str(self._get_medipim_response()))
            mock_post.return_value = response
            with patch.object(ProductProductMapper, "_get_image_content") as mock_image:
                mock_image.return_value = self._get_image()
                self.recordset.run_import()

        self.products = self._get_products() - self.product_before
        self.categories = self._get_categories() - self.categories_before

        self.assertEqual(2, len(self.products))
        self.assertEqual(0, len(self.categories))

        self.assertEqual(self.category, self.products[0].medipim_category_ids)

        recordset_values = self._get_recordset_values()
        self.assertRecordValues(
            self.products,
            recordset_values,
        )

    def test_update(self):
        self.products_before = self._get_products()
        self.products = self.env["product.product"].create(
            [
                {"name": "Product 1", "medipim_id": "M0000000001", "weight": 0.1},
                {"name": "Product 2", "medipim_id": "M0000000002", "weight": 0.15},
            ]
        )
        self.products.invalidate_recordset()
        # The product weight has changed
        with patch.object(requests, "post") as mock_post:
            response = Response()
            response.status_code = 200
            response.raw = StringIO(str(self._get_medipim_response(modified=True)))
            mock_post.return_value = response
            with patch.object(ProductProductMapper, "_get_image_content") as mock_image:
                mock_image.return_value = self._get_image()
                self.recordset.run_import()

        self.new_products = self._get_products() - self.products_before - self.products
        self.assertEqual(0, len(self.new_products))

        self.assertEqual([0.2, 0.16], self.products.mapped("weight"))
        self.assertEqual(["12348798", "12348799"], self.products.mapped("cnk_code"))
