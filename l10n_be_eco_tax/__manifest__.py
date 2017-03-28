# -*- coding: utf-8 -*-
# Copyright 2016 BCIM sprl(http://www.bcim.be)
# Copyright 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Belgium Eco Taxes",
    "summary": "Data module to support BEBAT and RECUPEL taxes",
    "version": "10.0.1.0.0",
    "author": "ACSONE SA/NV,"
              "BCIM sprl, "
              "Okia, "
              "Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "website": "http://odoo-community.org",
    "depends": ['account', 'l10n_be'],
    "data": [
        'data/account_tax_code_template.xml',
        'data/account_account_template_data.xml',
        'data/account_tax_template_recupel_out_data.xml',
        'data/account_tax_template_recupel_in_data.xml',
        'data/account_tax_template_bebat_data.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
}
