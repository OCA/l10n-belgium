# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Companyweb Business Information",
    "summary": (
        "Know exactly who you are doing business with. Enrich Odoo contacts with "
        "Companyweb."
    ),
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "version": "19.0.1.0.3",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "data": [
        "wizards/companyweb_search_wizard.xml",
        "wizards/companyweb_search_wizard_line.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "security/security.xml",
        "security/credential_wizard_security.xml",
        "security/search_wizard_security.xml",
        "views/partner_view.xml",
        "views/res_config_settings.xml",
        "wizards/credential_wizard.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
            "vcrpy-unittest",
        ],
    },
    "depends": ["contacts"],
    "maintainers": ["xavier-bouquiaux"],
    "application": True,
}
