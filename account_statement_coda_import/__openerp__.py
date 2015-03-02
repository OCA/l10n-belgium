# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{'name': "Bank statement CODA import",
 'version': '1.0',
 'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
 'maintainer': 'ACSONE SA/NV',
 'category': 'Finance',
 'complexity': 'normal',
 'depends': [
     'account_statement_base_import',
     'account_statement_bankaccount_completion'
 ],
 'description': """
Bank statement CODA import
==========================

This module brings generic methods and fields on bank statement to deal with
the importation of coded statement of account from electronic files. **CODA**

This is an alternative to the official l10n_be_coda that leverages the advanced
bank statement completion framework of the bank-statement-reconcile
OCA project (https://github.com/OCA/bank-statement-reconcile)

This module allows you to import your bank transactions with a standard
**CODA** file (you'll find samples in the 'data' folder). It respects the
chosen profile (model provided by the account_statement_ext module) to
generate the entries.

 .. important::
   The module requires the python library
   `pycoda <https://pypi.python.org/pypi/pycoda>`_
 """,
 'website': 'http://www.acsone.eu',
 'external_dependencies': {
     'python': ['coda'],
 },
 'init_xml': [],
 'update_xml': [
 ],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 }
