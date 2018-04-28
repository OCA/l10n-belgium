# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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

from openerp.tests.common import TransactionCase


class TestRegistryNumber(TransactionCase):

    def setUp(self):
        super(TestRegistryNumber, self).setUp()
        cr, uid = self.cr, self.uid
        self.rp_model = self.registry('res.partner')
        self.rp_id = self.registry('ir.model.data').get_object_reference(
            cr, uid, 'l10n_be_partner', 'res_partner_1')[1]

    def test_registry_number(self):
        cr, uid = self.cr, self.uid
        self.rp_model.write(cr, uid, [self.rp_id], {'vat': 'BE 0820 512 013'})
        rp = self.rp_model.browse(cr, uid, self.rp_id)
        self.assertEqual(rp.registry_authority, 'kbo_bce')
        self.assertEqual(rp.registry_number, '0820.512.013')
