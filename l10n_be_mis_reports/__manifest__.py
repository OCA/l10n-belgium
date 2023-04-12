# Copyright 2015-2018 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Belgium MIS Builder templates',
    'summary': """
        MIS Builder templates for the Belgium P&L,
        Balance Sheets and VAT Declaration""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-belgium',
    'category': 'Reporting',
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'depends': [
        'mis_builder',  # OCA/account-financial-reporting
        'l10n_be',
    ],
    'data': [
        'data/mis_report_styles.xml',
        'data/mis_report_bs_association_abridged.xml',
        'data/mis_report_bs_association_full.xml',
        'data/mis_report_bs_company_deprecated.xml',
        'data/mis_report_bs_company_wo_share_capital_abridged.xml',
        'data/mis_report_bs_company_wo_share_capital_full.xml',
        'data/mis_report_bs_company_wo_share_capital_micro.xml',
        'data/mis_report_pl_company_deprecated.xml',
        'data/mis_report_pl_company_wo_share_capital_abridged.xml',
        'data/mis_report_pl_company_wo_share_capital_full.xml',
        'data/mis_report_pl_company_wo_share_capital_micro.xml',
        'data/mis_report_vat.xml',
    ],
    'installable': True,
}
