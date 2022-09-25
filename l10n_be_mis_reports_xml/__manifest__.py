# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Belgium MIS Builder - XML exports",
    "summary": """
        Exports MIS Builder templates VAT Declaration as XML
        to load on the administration websites.""",
    "author": "Coop IT Easy SCRL," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "category": "Reporting",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "l10n_be_mis_reports",
        "report_xml",
    ],
    "data": [
        "data/data.xml",
        "reports/be_vat_declaration.xml",
        "views/mis_report_instance.xml",
        "wizards/be_vat_declaration_wizard.xml",
    ],
    "installable": True,
}
