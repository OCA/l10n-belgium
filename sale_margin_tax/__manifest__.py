# Copyright 2020 ACSONE SA/NV
# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Sale Margin Tax",
    "summary": """Sell used goods on the Belgian margin tax.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "len-foss,Financial Way,ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "depends": ["sale", "account"],
    "data": [
        "views/tax.xml",
        "data/account_tax.xml",
        "reports/report_invoice_document.xml",
    ],
}
