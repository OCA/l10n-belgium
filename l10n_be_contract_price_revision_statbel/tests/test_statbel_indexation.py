# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import requests_mock

from odoo.tests import SavepointCase

from odoo.addons.l10n_be_statbel_index.tests.test_statbel import directory


class TestStatbelIndexation(SavepointCase):
    @classmethod
    def _create_contract(cls):

        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
                "contract_type": "sale",
                "date": "2019-11-29",
                "date_start": "2019-11-29",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product_1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2019-11-29",
                            "recurring_next_date": "2019-11-29",
                        },
                    )
                ],
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_retrieval = cls.env["l10n_be.statbel.retrieval"].create({})
        cls.wizard = cls.env["l10n_be.statbel.indexation.computer"].new({})
        cls.revision_obj = cls.env["contract.price.revision.wizard"]
        cls.index = cls.env["l10n_be.statbel.index"]

        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "pricelist for contract test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test contract",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo@demo.com",
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")

        cls._create_contract()

    def test_statbel_indexation(self):
        """Import the current index values"""
        with requests_mock.mock() as r_mock:
            path = os.path.join(directory, "CPI All base years.xlsx")
            with open(path, "rb") as the_file:
                r_mock.get(self.wizard_retrieval.url, body=the_file)
                self.wizard_retrieval.retrieve_statbel()
        original_line = self.contract.contract_line_ids
        self.revision = self.revision_obj.with_context(
            active_ids=self.contract.ids
        ).create(
            {
                "variation_type": "l10n_be_statbel",
                "date_start": "2020-12-01",
                "belgium_region": "walloon",
            }
        )
        self.revision.action_apply()
        self.assertEqual(len(self.contract.contract_line_ids), 2)
        line_text = (
            "Contract line (Services from #START# to #END#) price has been revised"
        )
        modification = self.contract.modification_ids.filtered(
            lambda line: line.description.startswith(line_text)
        )
        self.assertEqual(1, len(modification))
        new_line = self.contract.contract_line_ids - original_line
        self.assertAlmostEqual(new_line.price_unit, 100.85)
