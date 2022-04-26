# Copyright 2015-2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestCodaFile(TransactionCase):
    """Tests for import bank statement coda file format
    (account.statement.import)
    """

    def setUp(self):
        super().setUp()
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "BE46737018594236",
                "bank_bic": "KREDBEBB",
                "partner_id": self.env.ref("base.main_partner").id,
                "company_id": self.env.ref("base.main_company").id,
                "bank_id": self.env.ref("base.res_bank_1").id,
            }
        )
        eur = self.env.ref("base.EUR")
        journal_vals = {
            "name": "Bank Journal - (test coda)",
            "code": "TBNK",
            "type": "bank",
            "bank_account_id": bank_account.id,
        }
        if self.env.company.currency_id != eur:
            # coda files are in EUR
            journal_vals.update({"currency_id": eur.id})
        self.journal = self.env["account.journal"].create(journal_vals)
        self.statement_import_model = self.env["account.statement.import"]
        self.bank_statement_model = self.env["account.bank.statement"]
        coda_file_path = get_module_resource(
            "account_statement_import_coda",
            "test_coda_file",
            "Ontvangen_CODA.2012-01-11-18.59.15.txt",
        )
        self.coda_file = base64.b64encode(open(coda_file_path, "rb").read())

    def test_coda_file_import(self):
        bank_statement_import = self.statement_import_model.create(
            {
                "statement_file": self.coda_file,
                "statement_filename": "Coda test file",
            }
        )
        bank_statement_import.import_file_button()
        bank_st_record = self.bank_statement_model.search([("name", "=", "2012/135")])[
            0
        ]
        self.assertEqual(
            float_compare(bank_st_record.balance_start, 11812.70, precision_digits=2),
            0,
        )
        self.assertEqual(
            float_compare(
                bank_st_record.balance_end_real, 13646.05, precision_digits=2
            ),
            0,
        )

        # check the note
        self.assertEqual(
            "Counter Party: PARTNER 2\n"
            "Counter Party Account: BE61310126985517\n"
            "Communication: +++240/2838/42818+++ "
            "001PARTNER 2MOLENSTRAAT 60 9340 LEDE",
            bank_st_record.line_ids[1].narration,
            "The note should contain informations on the counter part "
            "but also the communication for the information records that "
            "refer the movement record",
        )

    def test_coda_file_import_twice(self):
        bank_statement_import = self.statement_import_model.create(
            {
                "statement_file": self.coda_file,
                "statement_filename": "Coda test file",
            }
        )
        bank_statement_import.import_file_button()
        with self.assertRaises(UserError):
            bank_statement_import.import_file_button()
