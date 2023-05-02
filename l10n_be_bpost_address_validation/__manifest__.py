# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bpost address validation",
    "summary": (
        "Check the validity of your partner's addresses "
        "or make a change with a change proposal."
    ),
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/bpost_address_validation.xml",
        "views/res_partner.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "l10n_be_bpost_adress_validation/static/src/js/**/*",
            "web/static/src/libs/fontawesome/css/font-awesome.css",
            ("include", "web._assets_helpers"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            ("include", "web._assets_bootstrap"),
        ]
    },
    "installable": True,
}
