# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import base64
# import textwrap

from odoo.exceptions import UserError

# from odoo.addons.mail.tests.common import MailCommon
from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install_l10n", "post_install", "-at_install")
class TestSodaFile(AccountTestInvoicingCommon):  # , MailCommon
    # @AccountTestInvoicingCommon.setup_country('be')
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        vals_journal = {
            "name": "Salaries",
            "code": "sal",
            "type": "general",
            "company_id": cls.company.id,
            "import_soda": True,
        }
        cls.journal = cls.env["account.journal"].create(vals_journal)
        soda_file_path = "l10n_be_import_soda/tests/data/basic_example.xml"
        cls.soda_file_path = soda_file_path
        with file_open(soda_file_path, "rb") as soda_file:
            vals_attachment = {
                "name": "soda_file.xml",
                "mimetype": "application/xml",
                "raw": soda_file.read(),
                "res_model": False,
                "res_id": 0,
            }
        cls.attachment = cls.env["ir.attachment"].create(vals_attachment)

    def test_soda_file_import_raise_if_no_mapping(self):
        with self.assertRaises(UserError) as error:
            self.journal.create_document_from_attachment(self.attachment.ids)
        message = str(error.exception.args[0])
        self.assertIn("618220", message)

    def test_soda_file_import(self):
        # given: we need to map all accounts
        account_61 = self.env["account.account"].search([("code", "=", "611000")])
        account_61.soda_mapping = "618220"
        account_45 = self.env["account.account"].search([("code", "=", "450000")])
        account_45.soda_mapping = "4530,4540"

        # when: we import the soda file
        self.journal.create_document_from_attachment(self.attachment.ids)

        # we just created the journal so there shouldn't be only the new move
        move = self.env["account.move"].search([("journal_id", "=", self.journal.id)])
        # then: the move was created with good values, and linked to the attachment
        self.assertIn("8805214", move.soda_ref)
        self.assertEqual(len(move.line_ids), 3)
        self.assertEqual(self.attachment.res_id, move.id)

    def test_soda_file_import_auto_map(self):
        # given: we set auto map to True
        self.company.soda_auto_map = True
        # when: we import the soda file
        self.journal.create_document_from_attachment(self.attachment.ids)

        # we just created the journal so there shouldn't be only the new move
        move = self.env["account.move"].search([("journal_id", "=", self.journal.id)])
        # then: the move was created with good values, and linked to the attachment
        self.assertIn("8805214", move.soda_ref)
        # we have created the accounts
        account_618220 = self.env["account.account"].search([("code", "=", "618220")])
        self.assertEqual(account_618220.soda_mapping, "618220")
        self.assertEqual(account_618220.name, "Salaries")
