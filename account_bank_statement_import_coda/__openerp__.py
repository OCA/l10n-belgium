# -*- coding: utf-8 -*-
# Copyright 2015-2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Import CODA Bank Statement',
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://www.acsone.eu",
    'category': 'Accounting & Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account_bank_statement_import'
    ],
    'data': [
        'views/account_bank_statement_view.xml',
    ],
    'external_dependencies': {
        'python': ['coda'],
    },
    'auto_install': False,
    'installable': True,
}
