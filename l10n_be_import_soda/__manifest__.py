# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Belgium - Import SODA files",
    "summary": """Import SODA files.""",
    "author": "Lambdao, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "category": "Accounting/Localizations",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_account.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/res_config_settings_views.xml",
    ],
    "application": False,
    "installable": True,
}
