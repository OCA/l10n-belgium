# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "CodaBox",
    "category": "Accounting",
    "summary": "Connection to CodaBox",
    "website": "https://github.com/OCA/l10n-belgium",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "description": """
- Imports Coda files automatically through CodaBox
    """,
    "author": "Niboo SRL,Odoo Community Association (OCA)",
    "depends": ["l10n_be_coda"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/codabox.xml",
        "views/codabox_config_settings.xml",
        "wizards/codabox_credentials_wizard.xml",
    ],
    "installable": True,
    "application": False,
}
