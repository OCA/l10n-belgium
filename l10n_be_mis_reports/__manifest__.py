# Copyright 2015-2018 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Belgium MIS Builder templates",
    "summary": """
        MIS Builder templates for the Belgium P&L,
        Balance Sheets and VAT Declaration""",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "category": "Reporting",
    "version": "17.0.2.0.0",
    "license": "AGPL-3",
    "depends": ["mis_builder", "l10n_be"],  # OCA/account-financial-reporting
    "data": [
        "data/mis_report_styles.xml",
        "data/mis_report_bs_m01-f.xml",
        "data/mis_report_pl_m01-f.xml",
        "data/mis_report_bs_m02-f.xml",
        "data/mis_report_pl_m02-f.xml",
        "data/mis_report_bs_m04-f.xml",
        "data/mis_report_pl_m04-f.xml",
        "data/mis_report_bs_m05-f.xml",
        "data/mis_report_pl_m05-f.xml",
        "data/mis_report_bs_m07-f.xml",
        "data/mis_report_pl_m07-f.xml",
        "data/mis_report_bs_m08-f.xml",
        "data/mis_report_pl_m08-f.xml",
        "data/mis_report_bs_m81-f.xml",
        "data/mis_report_pl_m81-f.xml",
        "data/mis_report_bs_m82-f.xml",
        "data/mis_report_pl_m82-f.xml",
        "data/mis_report_bs_m87-f.xml",
        "data/mis_report_pl_m87-f.xml",
        "data/mis_report_bs_deprecated.xml",
        "data/mis_report_pl_deprecated.xml",
        "data/mis_report_vat.xml",
    ],
    "installable": True,
}
