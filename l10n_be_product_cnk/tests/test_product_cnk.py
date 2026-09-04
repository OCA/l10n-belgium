# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestProductCnk(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "cnk_code": "12345",
            }
        )

    def test_product_cnk(self):
        template = self.env["product.template"].search([("cnk_code", "=", "12345")])
        self.assertEqual(template.product_variant_ids, self.product)

        template.cnk_code = "54321"
        self.assertEqual(self.product.cnk_code, "54321")

        template.invalidate_recordset()
        self.assertEqual("54321", template.cnk_code)
