# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Companyweb Payment Info",
    "summary": ("Send your customer payment information to Companyweb"),
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "version": "16.0.1.0.4",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "installable": True,
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizards/payment_info_wizard.xml",
    ],
    "images": [
        "static/description/doc_companyweb_data.png",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
        ],
    },
    "depends": ["companyweb_base", "account"],
    "maintainers": ["xavier-bouquiaux"],
}
