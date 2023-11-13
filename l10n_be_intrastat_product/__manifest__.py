# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Intrastat Product Declaration for Belgium",
    "version": "15.0.1.0.0",
    "category": "Intrastat",
    "license": "AGPL-3",
    "summary": "Intrastat Product Declaration for Belgium",
    "author": "Noviat,Odoo Community Association (OCA)",
    "maintainers": ["luc-demeyer", "jdidderen-noviat"],
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["intrastat_product"],
    "conflicts": ["l10n_be_intrastat", "report_intrastat"],
    "data": [
        "security/intrastat_security.xml",
        "security/ir.model.access.csv",
        "data/intrastat_region.xml",
        "data/intrastat_transaction.xml",
        "views/account_move_views.xml",
        "views/l10n_be_intrastat_product_views.xml",
    ],
    "installable": True,
}
