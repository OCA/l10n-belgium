# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import requests_mock

from odoo.tests import SavepointCase

directory = os.path.dirname(__file__)


class TestStatBelIndexation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_retrieval = cls.env["l10n_be.statbel.retrieval"].create({})
        cls.wizard = cls.env["l10n_be.statbel.indexation.computer"].new({})
        cls.index = cls.env["l10n_be.statbel.index"]

    def test_statbel_indexation(self):
        """Import the current index values"""
        with requests_mock.mock() as r_mock:
            path = os.path.join(directory, "CPI All base years.xlsx")
            with open(path, "rb") as the_file:
                r_mock.get(self.wizard_retrieval.url, body=the_file)
                self.wizard_retrieval.retrieve_statbel()

        # Set contract date, walloon region, compute date for 01/12/2020
        # Initial index should be 108.98
        # Actual index should be 109.91
        self.wizard.contract_date = "2019-11-29"
        self.wizard.region = "walloon"
        self.wizard.original_price = 1000
        self.wizard.compute_date = "2020-12-01"
        self.assertEquals(self.wizard.reference_month, "10/2019")
        self.assertEquals(self.wizard.base_year, "2013")
        self.assertEquals(108.98, self.wizard.reference_index_id.index_value)
        self.assertEquals(109.91, self.wizard.actual_index_id.index_value)
        self.assertEquals(1008.53, self.wizard.computed_price)
