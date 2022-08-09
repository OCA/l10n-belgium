# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n Be Contract Price Revision Statbel",
    "summary": """
        Allows to revise contract price depending on Statbel indexes""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": [
        "contract_price_revision",
        "l10n_be_statbel_index",
    ],
    "data": [
        "wizards/contract_price_revision_wizard.xml",
    ],
}
