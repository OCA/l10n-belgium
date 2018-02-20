# -*- coding: utf-8 -*-
# Copyright 2015-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Import Bpost Bank Statements',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'summary': 'Import Bpost (Belgian Post) CSV bank statement files',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-belgium',
    'depends': ['account_bank_statement_import'],
    'external_dependencies': {'python': ['unicodecsv']},
    'data': ['wizard/account_bank_statement_import_view.xml'],
    'installable': True,
}
