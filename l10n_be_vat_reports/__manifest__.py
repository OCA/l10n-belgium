# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Belgium VAT Reports",
    "author": "ACSONE SA/NV, "
    "Coop IT Easy SC, "
    "Odoo SA, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "category": "Reporting",
    "version": "16.0.1.0.3",
    "license": "AGPL-3",
    "depends": [
        "l10n_be",
        "account",
        "report_xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/be_vat_client_listing_consignment.xml",
        "reports/be_vat_declarant.xml",
        "reports/be_vat_intra_consignment.xml",
        "wizard/partner_vat_list_views.xml",
        "wizard/l10n_be_vat_intra_view.xml",
        "views/report_vatintraprint.xml",
        "views/report_vatpartnerlisting.xml",
        "reports/l10n_be_reports.xml",
    ],
}
