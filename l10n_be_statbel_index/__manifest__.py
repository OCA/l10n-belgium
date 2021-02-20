# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n Be Statbel Index",
    "summary": """
        Allows to retrieve Statbel health indices""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["base"],
    "data": [
        "security/l10n_be_statbel_index.xml",
        "views/l10n_be_statbel_index.xml",
        "wizards/indexation_computer.xml",
        "data/ir_cron.xml",
    ],
    "external_dependencies": {"python": ["openpyxl"]},
}
