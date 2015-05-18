# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of l10n_be_mis_reports,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     l10n_be_mis_reports is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     l10n_be_mis_reports is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with l10n_be_mis_reports.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "l10n_be_mis_reports",

    'summary': """
        MIS Report templates for the Belgium P&L and Balance Sheets""",

    # 'description': put the module description in README.rst

    'author': "ACSONE SA/NV",
    'website': "http://acsone.eu",

    # Categories can be used to filter modules in modules listing
    # Check http://goo.gl/0TfwzD for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'mis_builder',
    ],

    # always loaded
    'data': [
        'data/mis_report_pl.xml',
        'data/mis_report_bs.xml',
    ],
}
