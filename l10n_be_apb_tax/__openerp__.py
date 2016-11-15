# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Jacques-Etienne Baudoux
#    Copyright (c) 2016 BCIM (http://www.bcim.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Belgium APB Taxes",
    "summary": "Data module to support APB taxes",
    "version": "9.0.1.0.0",
    "author": "BCIM sprl, "
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
