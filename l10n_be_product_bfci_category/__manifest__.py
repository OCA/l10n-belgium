# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Belgian Product BFCI Category",
    "summary": """This module allows to define a CBIP/BFCI category on products""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["product", "product_usability"],
    "data": [
        "security/product_category_bfci.xml",
        "views/product_category_bfci.xml",
        "views/product_template.xml",
    ],
    "demo": [
        "demo/product_category_bfci.xml",
    ],
}
