# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from openerp.exceptions import ValidationError


class TestL10nBeIso20022Pain(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestL10nBeIso20022Pain, cls).setUpClass()

        # MODELS
        cls.invoice_model = cls.env['account.invoice']
        cls.account_model = cls.env['account.account']
        cls.invoice_line_model = cls.env['account.invoice.line']
        cls.payment_line_model = cls.env['account.payment.line']
        cls.payment_mode_model = cls.env['account.payment.mode']
        cls.journal_model = cls.env['account.journal']

        # INSTANCES
        # Instance: Account
        cls.invoice_account = cls.account_model.search(
            [('user_type_id',
              '=',
              cls.env.ref('account.data_account_type_receivable').id
              )], limit=1)
        # Instance: Invoice Line
        cls.invoice_line = cls.invoice_line_model.create(
            {'name': 'Test invoice line',
             'account_id': cls.invoice_account.id,
             'quantity': 2.000,
             'price_unit': 2.99})
        # Instance: Account (sales)
        cls.account_sales = cls.account_model.create({
            'code': "X1020",
            'name': "Product Sales - (test)",
            'user_type_id': cls.env.ref(
                'account.data_account_type_revenue').id
        })
        # Instance: Journal
        cls.sales_journal = cls.journal_model.create({
            'name': "Sales Journal - (test)",
            'code': "TSAJ",
            'type': "sale",
            'refund_sequence': True,
            'default_debit_account_id': cls.account_sales.id,
            'default_credit_account_id': cls.account_sales.id,
        })
        # Instance: Payment Mode
        cls.payment_mode = cls.payment_mode_model.create({
            'name': 'Test payment mode',
            'payment_method_id': cls.env.ref(
                'account.account_payment_method_manual_out').id,
            'fixed_journal_id': cls.sales_journal.id,
            'bank_account_link': 'fixed'})
        # Instance: Invoice
        cls.invoice = cls.invoice_model.create({
            'partner_id': cls.env.ref('base.res_partner_2').id,
            'account_id': cls.invoice_account.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(6, 0, [cls.invoice_line.id])],
            'reference_type': 'bba',
            'reference': '+++868/0542/73023+++',
            'state': 'open',
            'payment_mode_id': cls.payment_mode.id})

    def _prepare_payment_line_creation_dict(self):
        return {
            'currency_id': self.env.ref('base.EUR').id,
            'partner_id': self.env.ref('base.res_partner_2').id,
            'communication_type': 'bba',
            'amount_currency': 123.321,
        }

    def test_create_account_payment_line_01(self):
        """
        Data:
            - A draft valid draft invoice with BBA communication
        Test case:
            - Open the invoice
            - Prepare payment
        Expected result:
            - The created payment line takes the BBA communication
        """
        self.invoice.action_move_create()
        self.invoice.create_account_payment_line()
        pl = self.payment_line_model.search(
            [('move_line_id.invoice_id', '=', self.invoice.id)], limit=1)
        self.assertEqual(pl.communication, '868054273023')

    def test_create_account_payment_line_02(self):
        """
        Data:
            - No invoice, no payment line, nothing
        Test case:
            - Create a new payment line with invalid BBA communication
        Expected result:
            - ValidationError
        """
        vals = self._prepare_payment_line_creation_dict()
        vals['communication'] = '868054273024'
        with self.assertRaises(ValidationError):
            self.payment_line_model.create(vals)

    def test_create_account_payment_line_03(self):
        """
        Data:
            - No invoice, no payment line, nothing
        Test case:
            - Create a new payment line with invalid BBA communication
              (too short)
        Expected result:
            - ValidationError
        """
        vals = self._prepare_payment_line_creation_dict()
        vals['communication'] = '8680542730241'
        with self.assertRaises(ValidationError):
            self.payment_line_model.create(vals)

    def test_create_account_payment_line_04(self):
        """
        Data:
            - No invoice, no payment line, nothing
        Test case:
            - Create a new payment line with invalid BBA communication
              (too long)
        Expected result:
            - ValidationError
        """
        vals = self._prepare_payment_line_creation_dict()
        vals['communication'] = '86805427302'
        with self.assertRaises(ValidationError):
            self.payment_line_model.create(vals)

    def test_create_account_payment_line_05(self):
        """
        Data:
            - No invoice, no payment line, nothing
        Test case:
            - Create a new payment line with valid BBA communication
        Expected result:
            - The payment line is created with the valid communication
        """
        vals = self._prepare_payment_line_creation_dict()
        vals['communication'] = '868054273023'
        self.payment_line_model.create(vals)
