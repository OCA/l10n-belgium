# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Companyweb",
    "summary": (
        "Know who you are dealing with. "
        "Enhance Odoo partner data from companyweb.be."
    ),
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "version": "14.0.1.0.3",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/partner_view.xml",
        "wizards/credential_wizard.xml",
    ],
    "images": [
        "static/description/main_screenshot.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
        ],
    },
    "depends": ["web_notify"],
    "maintainers": ["xavier-bouquiaux"],
}
