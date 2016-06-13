# -*- coding: utf-8 -*-
# Copyright 2015-2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.modules.module import get_module_resource
from openerp.tools import float_compare


class TestCodaFile(TransactionCase):
    """Tests for import bank statement coda file format
    (account.bank.statement.import)
    """

    def setUp(self):
        super(TestCodaFile, self).setUp()
        self.env['res.partner.bank'].create({
            'state': 'bank',
            'acc_number': 'BE46737018594236',
            'bank_bic': 'KREDBEBB',
            'journal_id': self.ref('account.bank_journal'),
            'partner_id': self.ref('base.main_partner'),
        })
        fy = self.env['account.fiscalyear'].create({
            'name': 'FY 2012',
            'code': '2012',
            'date_start': '2012-01-01',
            'date_stop': '2012-12-31',
            'company_id': self.ref('base.main_company'),
        })
        self.env['account.period'].create({
            'name': 'FP 2012-01',
            'code': '2012-01',
            'date_start': '2012-01-01',
            'date_stop': '2012-01-31',
            'fiscalyear_id': fy.id,
            'company_id': self.ref('base.main_company'),
        })
        self.statement_import_model = self.env[
            'account.bank.statement.import']
        self.bank_statement_model = self.env['account.bank.statement']
        coda_file_path = get_module_resource(
            'account_bank_statement_import_coda',
            'test_coda_file',
            'Ontvangen_CODA.2012-01-11-18.59.15.txt')
        self.coda_file = open(coda_file_path, 'rb').read().encode('base64')
        self.context = {
            'journal_id': self.ref('account.bank_journal')
        }
        self.bank_statement_import = self.statement_import_model.create(
            {'data_file': self.coda_file})

    def test_coda_file_import(self):
        self.bank_statement_import.import_file()
        bank_st_record = self.bank_statement_model.search([
            ('name', '=', 'TBNK/2012/135')])[0]
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
        # check line name
        self.assertEqual(
            'MEDEDELING', bank_st_record.line_ids[0].name,
            'Name should be the communication if no structured communication '
            'found')
        self.assertEqual(
            '+++240/2838/42818+++', bank_st_record.line_ids[1].name,
            'Name should be the structured communication id provided')
        for line in bank_st_record.line_ids[2:5]:
            self.assertEqual(
                'KBC-INVESTERINGSKREDIET 737-6543210-21', line.name,
                'Name should be the communication of the related '
                'globalisation line for details line')

        # check the note
        self.assertEqual(
            'Counter Party: PARTNER 2\n'
            'Counter Party Account: BE61310126985517\n'
            'Communication: +++240/2838/42818+++ '
            '001PARTNER 2MOLENSTRAAT 60 9340 LEDE',
            bank_st_record.line_ids[1].note,
            'The note should contain informations on the counter part '
            'but also the communication for the information records that '
            'refer the movement record'
            )

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
