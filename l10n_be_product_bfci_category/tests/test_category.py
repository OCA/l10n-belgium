# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestCategory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["product.bfci.category"]
        cls.category_1 = cls.model.create(
            {
                "name": "Drugs",
            }
        )
        cls.category_1_1 = cls.model.create(
            {
                "name": "Fever",
                "parent_id": cls.category_1.id,
            }
        )

    def test_name(self):
        self.assertEqual("Drugs / Fever", self.category_1_1.complete_name)
