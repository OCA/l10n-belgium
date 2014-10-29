# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import base64
import inspect
import os

from openerp.osv.osv import except_osv
from openerp.tests import common


class test_coda_import(common.TransactionCase):

    def setUp(self):
        super(test_coda_import, self).setUp()
        self.company_a = self.browse_ref('base.main_company')
        self.profile_obj = self.registry('account.statement.profile')
        self.acc_bk_stm_obj = self.registry('account.bank.statement')
        # create the 2009 fiscal year since imported coda file reference
        # statement lines in 2009
        self.fiscalyear_id = self._create_fiscalyear('2009', self.company_a.id)

        self.account_id = self.ref('account.a_recv')
        self.journal_id = self.ref('account.bank_journal')
        self.import_wizard_obj = self.registry('credit.statement.import')
        self.profile_id = self.profile_obj.create(self.cr, self.uid, {
            'name': 'CODA_PROFILE',
            'commission_account_id': self.account_id,
            'journal_id': self.journal_id,
            'import_type': 'coda_transaction'})

    def _create_fiscalyear(self, year, company_id):
        fiscalyear_obj = self.registry('account.fiscalyear')
        fiscalyear_id = fiscalyear_obj.create(self.cr, self.uid, {
            'name': year,
            'code': year,
            'date_start': year + '-01-01',
            'date_stop': year + '-12-31',
            'company_id': company_id
        })
        fiscalyear_obj.create_period3(self.cr, self.uid, [fiscalyear_id])
        return fiscalyear_id

    def _to_abs_filename(self, file_name):
        dir_name = os.path.dirname(inspect.getfile(self.__class__))
        return os.path.join(dir_name, file_name)

    def _import_coda_file(self, file_name):
        """ import a coda file using the wizard
        return the create account.bank.statement object
        """
        with open(file_name) as f:
            content = f.read()
            wizard_id = self.import_wizard_obj.create(self.cr, self.uid, {
                'profile_id': self.profile_id,
                'input_statement': base64.b64encode(content),
                'file_name': os.path.basename(file_name),
            })
            res = self.import_wizard_obj.import_statement(self.cr,
                                                          self.uid,
                                                          wizard_id)
            statement_ids = self.acc_bk_stm_obj.search(self.cr,
                                                       self.uid,
                                                       eval(res['domain']))
            return self.acc_bk_stm_obj.browse(self.cr, self.uid, statement_ids)

    def _add_res_bank(self, statement_acc_number):
        res_bank_obj = self.registry('res.partner.bank')
        partner_id = self.ref('base.main_partner')
        res_bank_id = res_bank_obj.create(self.cr,
                                          self.uid,
                                          {'name': 'test',
                                           'state': 'bank',
                                           'acc_number': statement_acc_number,
                                           'partner_id': partner_id})
        res_bank_obj.write(self.cr,
                           self.uid,
                           res_bank_id,
                           {'journal_id': self.journal_id})

    def test_statement_validation(self):
        """Test import from CODA 2.3
        """
        statement_acc_number = 'BE86407051416150'
        partner_id = self.ref('base.main_partner')
        file_name = self._to_abs_filename(
            'Coda_iban_v2_3_single_statement.txt')
        # try to import a Coda file with a statement bank account not defined
        # in the system
        with self.assertRaisesRegexp(except_osv,
                                     "(u'Not supported CODA file', u'No "
                                     "matching Bank Account found for the "
                                     "statement account number found in file "
                                     "BE86407051416150')"):
            self._import_coda_file(file_name)
        # try to import a Coda file referencing a bank statement without
        # journal
        res_bank_obj = self.registry('res.partner.bank')
        res_bank_id = res_bank_obj.create(self.cr,
                                          self.uid,
                                          {'name': 'test',
                                           'state': 'bank',
                                           'acc_number': statement_acc_number,
                                           'partner_id': partner_id})
        with self.assertRaisesRegexp(except_osv,
                                     "(u'Not supported CODA file', u\"No "
                                     "Account Journal defined for "
                                     "bank account "
                                     "named \'test\' for account number "
                                     "\'BE86407051416150\'\")"):
            self._import_coda_file(file_name)

        # try to import a Coda file referencing a bank statement with a bank
        # account not referencing the right journal
        res_bank_obj.write(self.cr,
                           self.uid,
                           res_bank_id,
                           {'journal_id': self.ref('account.cash_journal')})
        with self.assertRaisesRegexp(except_osv,
                                     "(u'Not supported CODA file', "
                                     "u\"The journ"
                                     "al \'Cash Journal - \(test\) \(EUR\)\' "
                                     "on the Bank Account \'test\' doesn\'t "
                                     "match the journal \'Bank Journal - "
                                     "\(test\)\' on the profile\")"):
            self._import_coda_file(file_name)

    def test_signle_statement_import(self):
        self._add_res_bank('BE86407051416150')
        file_name = self._to_abs_filename(
            'Coda_iban_v2_3_single_statement.txt')
        statements = self._import_coda_file(file_name)
        self.assertEqual(1, len(statements))
        statement = statements[0]
        self.assertEqual('2009/042', statement.name)
        self.assertEqual(0.0, statement.balance_start)
        self.assertEqual(0.0, statement.balance_end_real)
        self.assertEqual('2009-03-05', statement.date)
        self.assertEqual(30, len(statement.line_ids))
        self.assertEqual(statement.balance_end_real, statement.balance_end)
        for st_line_obj in statement.line_ids:
            if st_line_obj['ref'] == '00170005':
                # common infos
                self.assertEqual(st_line_obj['name'],
                                 'OVERBOEKING NAAR CENTRALE '
                                 'REKENING\nOVERBOEKING NAAR '
                                 'CENTRALE REKENING')
                self.assertEqual(st_line_obj['amount'], -15.0)
                # additional info provided by CODA
                # check that the bank information are correctly filled
                # on the statement line
                self.assertEqual(st_line_obj['partner_acc_number'],
                                 'BE38733040385372')
                return
        self.fail('No statement line found with ref \'0017000\'')

    def test_multi_statements_import(self):
        self._add_res_bank('BE13001676096039')
        file_name = self._to_abs_filename(
            'Coda_iban_v2_3_multi_statements.txt')
        statements = self._import_coda_file(file_name)
        self.assertEqual(2, len(statements))
        if statements[0].name == '2014/037':
            statement_2014_037 = statements[0]
            statement_2014_036 = statements[1]
        else:
            statement_2014_037 = statements[1]
            statement_2014_036 = statements[0]

        self.assertEqual(1, len(statement_2014_037.line_ids))
        self.assertEqual(1, len(statement_2014_036.line_ids))

        self.assertEqual(statement_2014_036.name, '2014/036')
        self.assertEqual('2014-03-29', statement_2014_036.date)
        self.assertEqual(39698.09, statement_2014_036.balance_start)
        self.assertEqual(39575.69, statement_2014_036.balance_end)
        self.assertEqual(statement_2014_036.balance_end_real,
                         statement_2014_036.balance_end)

        self.assertEqual(statement_2014_037.name, '2014/037')
        self.assertEqual('2014-03-31', statement_2014_037.date)
        self.assertEqual(39575.69, statement_2014_037.balance_start)
        self.assertEqual(139575.69, statement_2014_037.balance_end)
        self.assertEqual(statement_2014_037.balance_end_real,
                         statement_2014_037.balance_end)
