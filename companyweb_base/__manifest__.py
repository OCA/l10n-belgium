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
    "version": "17.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "data": [
        "data/ir_config_parameter.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/partner_view.xml",
        "wizards/credential_wizard.xml",
    ],
    "images": [
        "static/description/doc_companyweb_data.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
        ],
    },
    "depends": ["contacts"],
    "maintainers": ["xavier-bouquiaux"],
}
