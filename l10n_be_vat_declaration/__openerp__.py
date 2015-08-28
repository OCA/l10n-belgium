# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2009-2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Belgium - VAT Declaration',
    'version': '1.6',
    'license': 'AGPL-3',
    'author': "Noviat, Odoo Community Association (OCA)",
    'website': 'http://www.noviat.com',
    'category': 'Localization',
    'depends': [
        'account',
        'base_vat',
    ],
    'data': [
        'views/menu.xml',
        'data/l10n_be_sequence.xml',
        'wizards/reports.xml',
        'wizards/l10n_be_vat_declaration_view.xml',
        'wizards/l10n_be_vat_intra_view.xml',
        'wizards/l10n_be_partner_vat_listing.xml',
        'views/l10n_be_layouts.xml',
        'views/report_l10nbevatdeclaration.xml',
        'views/report_l10nbevatlisting.xml',
        'views/report_l10nbevatintra.xml',
    ],
    'installable': True,
}
