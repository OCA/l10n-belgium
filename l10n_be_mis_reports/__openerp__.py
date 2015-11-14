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
    'name': 'Belgium MIS Builder templates',
    'summary': """
        MIS Builder templates for the Belgium P&L and Balance Sheets""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'http://acsone.eu',
    'category': 'Reporting',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'mis_builder',  # OCA/account-financial-reporting
    ],
    'data': [
        'data/mis_report_pl.xml',
        'data/mis_report_bs.xml',
    ],
}
