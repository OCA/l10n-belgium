# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Author: Adrien Peiffer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Companyweb",
    "version": "10.0.1.0.0",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "website": "http://www.acsone.eu",
    "depends": [
        'base_vat',
        # TODO: account voucher is required
        #       for the test suite only
        #       (need to refactor the test suite)
        # 'account_voucher',
    ],
    'external_dependencies': {
        'python': ['lxml', 'xlwt', 'xlrd'],
    },
    "description": """
Companyweb - Know who you are dealing with
==========================================

This module provides access to financial health information about Belgian
companies right from the OpenERP Customer form. Information is obtained
from the Companyweb database (www.companyweb.be).

You must be a Companyweb customer to use this module in production.
Please visit www.companyweb.be and use login 'cwacsone',
with password 'demo' to obtain test credentials.

Main Features
-------------
* Obtain crucial information about Belgian companies,
  based on their VAT number: name, address,
  credit limit, health barometer, financial informations
  such as turnover or equity capital, and more.
* Update address and credit limit in your OpenERP database.
* Generate reports about payment habits of your customers.
* Access to detailed company information on www.companyweb.be.

Technical information
---------------------
This module depends on module account_financial_report_webkit which
provides an accurate algorithm for open invoices report.

Contributors
------------
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Pascal Vanderperre <pascal.vanderperre@noviat.com>
* Luc De Meyer <luc.demeyer@noviat.com>
""",
    "data": [
        "wizard/account_companyweb_report_wizard_view.xml",
        "wizard/account_companyweb_wizard_view.xml",
        "view/res_config_view.xml",
        "view/res_partner_view.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
    "installable": True,
}
