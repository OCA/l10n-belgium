# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# Copyright (c) 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Companyweb",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV,BCIM sprl,Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "depends": [
        'account_financial_report_webkit',
        'base_vat',
        'account',
        # TODO: account voucher is required
        #       for the test suite only
        #       (need to refactor the test suite)
        'account_voucher',
    ],
    'external_dependencies': {
        'python': ['lxml', 'xlwt', 'xlrd'],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/companyweb_history.xml",
        "views/res_config_view.xml",
        "views/res_partner_view.xml",
        "wizard/partner_update_companyweb.xml",
        "wizard/companyweb_follow_customer.xml",
        "data/cron_fetch_new_modification.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
    "installable": True,
}
