# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Import CODA Bank Statement',
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/l10n-belgium",
    'category': 'Accounting & Finance',
    'version': '11.0.1.0.2',
    'license': 'AGPL-3',
    'depends': [
        'account_bank_statement_import',
    ],
    'data': [
        'wizard/account_bank_statement_import_coda_view.xml',
    ],
    'external_dependencies': {
        'python': ['coda'],
    },
    'auto_install': False,
    'installable': True,
}
