# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "L10n Be Connector Importer Source Medipim Cbip",
    "summary": """This module allows to import CBIP categories and add it
    on products""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": [
        "l10n_be_product_bfci_category",
        "l10n_be_connector_importer_source_medipim",
    ],
    "data": [
        "data/source_medipim.xml",
        "data/import_type_product_product.xml",
        "data/import_recordset.xml",
    ],
    "demo": [],
}
