# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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
    "name": "Belgium Eco Taxes",
    "summary": "Data module to support BEBAT and RECUPEL taxes",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "category": "Generic Modules/Accounting",
    "website": "http://www.acsone.eu",
    "depends": ['account', 'l10n_be'],
    "data": [
        'data/account_tax_code_template.xml',
        'data/account_account_template_data.xml',
        'data/account_tax_template_recupel_out_data.xml',
        'data/account_tax_template_recupel_in_data.xml',
        'data/account_tax_template_bebat_data.xml',
    ],
    "demo": [],
    "license": "AGPL-3",
    "installable": True,
}
