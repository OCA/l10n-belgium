#  ©  2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestL10nBePartnerIdentification(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "company_type": "person",
            }
        )
        cls.national_registry_category = cls.env.ref(
            "l10n_be_partner_identification.l10n_be_national_registry_number_category"
        )
        cls.id_card_category = cls.env.ref(
            "l10n_be_partner_identification.l10n_be_id_card_category"
        )

    def test_validate_national_registry_number(self):
        partner_id_category = self.national_registry_category
        partner_1 = self.partner
        # born before 2000
        partner_1.write(
            {
                "id_numbers": [
                    (
                        0,
                        0,
                        {
                            "name": "85.01.01-002.14",
                            "category_id": partner_id_category.id,
                        },
                    )
                ]
            }
        )
        id_number = partner_1.id_numbers[0]
        self.assertEqual(id_number.name, "85.01.01-002.14")
        # born after 2000
        id_number.write(
            {"name": "08.03.25-264.77", "category_id": partner_id_category.id}
        )
        self.assertEqual(id_number.name, "08.03.25-264.77")
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid for a person born before 2000
            id_number.name = "85.01.01-002.03"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid for a person born after 2000
            id_number.name = "07.01.16-234.52"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid: too few digits after stripping non-digit chars
            id_number.name = "85.01.01"
        # check valid: check digit is 97 (seq % 97 == 0)
        id_number.write(
            {"name": "30.00.00-048.97", "category_id": partner_id_category.id}
        )
        self.assertEqual(id_number.name, "30.00.00-048.97")

    def test_validate_id_card(self):
        partner_id_category = self.id_card_category
        partner_1 = self.partner
        # born before 2000
        partner_1.write(
            {
                "id_numbers": [
                    (
                        0,
                        0,
                        {
                            "name": "000-0000000-97",
                            "category_id": partner_id_category.id,
                        },
                    )
                ]
            }
        )
        id_number = partner_1.id_numbers[0]
        self.assertEqual(id_number.name, "000-0000000-97")
        # born after 2000
        id_number.write(
            {"name": "000-0000001-01", "category_id": partner_id_category.id}
        )
        self.assertEqual(id_number.name, "000-0000001-01")
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid id number
            id_number.name = "000-0000001-02"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            # check invalid: too few digits after stripping non-digit chars
            id_number.name = "000-0000001"
