# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bpost address autocomplete",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["base", "web"],
    "data": [
        "views/res_partner.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_be_bpost_address_autocomplete/static/src/js/**/*",
            "web/static/src/libs/fontawesome/css/font-awesome.css",
            ("include", "web._assets_helpers"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            ("include", "web._assets_bootstrap"),
        ]
    },
    "installable": True,
}
