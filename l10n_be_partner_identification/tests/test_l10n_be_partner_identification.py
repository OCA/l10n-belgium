# -*- coding: utf-8 -*-
#  ©  2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common
from openerp.exceptions import ValidationError


class TestL10nBePartnerIdentification(common.TransactionCase):

    def test_validate_national_registry_number(self):
        partner_id_category = self.env.ref(
            'l10n_be_partner_identification.'
            'l10n_be_national_registry_number_category')
        partner_1 = self.env.ref('base.res_partner_1')
        # born before 2000
        partner_1.write({'id_numbers':  [(0, 0,  {
            'name': '85.01.01-002.14',
            'category_id': partner_id_category.id
        })]})
        id_number = partner_1.id_numbers[0]
        self.assertEqual(id_number.name, '85.01.01-002.14')
        # born after 2000
        id_number.write({'name': '07.01.16-234.22',
                         'category_id': partner_id_category.id})
        self.assertEqual(id_number.name, '07.01.16-234.22')
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid for a person born before 2000
            id_number.name = '85.01.01-002.03'
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid for a person born after 2000
            id_number.name = '07.01.16-234.52'
