# -*- coding: utf-8 -*-
# Copyright 2016 BCIM sprl(http://www.bcim.be)
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Belgium APB Taxes",
    "summary": "Data module to support APB taxes",
    "version": "10.0.1.0.0",
    "author": "BCIM sprl, "
              "Okia, "
              "Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "website": "http://odoo-community.org",
    "depends": ['account', 'l10n_be'],
    "data": [
        'data/account_tax_code_template.xml',
        'data/account_account_template_data.xml',
        'data/account_tax_template_apb_data.xml',
        'data/account_fiscal_position_tax_template.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
}
