# -*- coding: utf-8 -*-
# © 2015-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Import Bpost Bank Statements',
    'version': '8.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'summary': 'Import Bpost (Belgian Post) CSV bank statement files',
    'depends': ['account_bank_statement_import'],
    'external_dependencies': {'python': ['unicodecsv']},
    'installable': True,
}
