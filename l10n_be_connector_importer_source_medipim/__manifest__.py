# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "L10n Be Connector Importer Product Medipim",
    "summary": """This module allows to import products from Belgian Medipim API""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "maintainers": ["rousseldenis"],
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": [
        "connector_importer_product",
        "connector_importer_api",
        "l10n_be_product_cnk",
        "product_state",
        "product_usability",
    ],
    "data": [
        "security/security.xml",
        "data/product_tag.xml",
        "data/source_medipim.xml",
        "data/import_type_product_product.xml",
        "data/import_type_product_medipim_category.xml",
        "data/import_backend.xml",
        "data/import_recordset.xml",
        "views/product_tag.xml",
        "views/product_product.xml",
        "views/product_template.xml",
        "views/product_medipim_category.xml",
    ],
}
