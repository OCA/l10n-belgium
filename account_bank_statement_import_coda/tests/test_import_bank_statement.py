from openerp.tests.common import TransactionCase
from openerp.modules.module import get_module_resource
from openerp.tools import float_compare


class TestCodaFile(TransactionCase):
    """Tests for import bank statement coda file format
    (account.bank.statement.import)
    """

    def setUp(self):
        super(TestCodaFile, self).setUp()
        self.statement_import_model = self.env[
            'account.bank.statement.import']
        self.bank_statement_model = self.env['account.bank.statement']
        coda_file_path = get_module_resource(
            'account_bank_statement_import_coda',
            'test_coda_file',
            'Ontvangen_CODA.2013-01-11-18.59.15.txt')
        self.coda_file = open(coda_file_path, 'rb').read().encode('base64')
        self.context = {
            'journal_id': self.ref('account.bank_journal')
        }
        self.bank_statement_import = self.statement_import_model.create(
            {'data_file': self.coda_file})

    def test_coda_file_import(self):
        self.bank_statement_import.import_file()
        bank_st_record = self.bank_statement_model.search([
            ('name', '=', '2011/135')])[0]
        self.assertEqual(
            float_compare(
                bank_st_record.balance_start,
                11812.70,
                precision_digits=2),
            0)
        self.assertEqual(
            float_compare(
                bank_st_record.balance_end_real,
                13646.05,
                precision_digits=2),
            0)

    def test_coda_file_import_twice(self):
        self.bank_statement_import.import_file()
        with self.assertRaises(Exception):
            self.bank_statement_import.import_file()

    def test_coda_file_wrong_journal(self):
        """ The demo account used by the CODA file is linked to the
        demo bank_journal """
        bank_statement_import = self.statement_import_model.create(
            {'data_file': self.coda_file}).with_context(
                journal_id=self.ref('account.check_journal'))
        with self.assertRaises(Exception):
            bank_statement_import.import_file()
