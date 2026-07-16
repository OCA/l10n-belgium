# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Companyweb Payment Info",
    "summary": "Send your customer payment information to Companyweb",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "version": "19.0.1.0.2",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/res_config_settings.xml",
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
