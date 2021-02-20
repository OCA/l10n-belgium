# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import requests_mock

from odoo.exceptions import UserError
from odoo.tests import SavepointCase

directory = os.path.dirname(__file__)


class TestStatBel(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env["l10n_be.statbel.retrieval"].create({})
        cls.index = cls.env["l10n_be.statbel.index"]

    def test_statbel(self):
        indexes_before = self.index.search_count([])
        self.assertFalse(indexes_before)
        with requests_mock.mock() as r_mock:
            path = os.path.join(directory, "CPI All base years.xlsx")
            with open(path, "rb") as the_file:
                r_mock.get(self.wizard.url, body=the_file)
                self.wizard.retrieve_statbel()

            indexes_after = self.index.search_count([])
            self.assertTrue(indexes_before < indexes_after)
            with open(path, "rb") as the_file:
                r_mock.get(self.wizard.url, body=the_file)
                self.wizard.retrieve_statbel()
            indexes_after_2 = self.index.search_count([])
            self.assertEqual(indexes_after, indexes_after_2)

    def test_statbel_error(self):
        with requests_mock.mock() as r_mock:
            path = os.path.join(directory, "CPI All base years.xlsx")
            with open(path, "rb"):
                r_mock.get(self.wizard.url, text="Not Found", status_code=404)
                with self.assertRaises(UserError, msg="Not Found"):
                    self.wizard.retrieve_statbel()
