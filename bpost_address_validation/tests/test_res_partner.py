from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.belgium = cls.env["res.country"].search([("code", "=", "BE")])
        cls.luxembourg = cls.env["res.country"].search([("code", "=", "LU")])

        cls.partner_be = cls.env["res.partner"].create(
            {
                "name": "Acsone",
                "street": "Quai Banning 6",
                "city": "Liège",
                "zip": "4000",
                "country_id": cls.belgium.id,
            }
        )

        cls.partner_lu = cls.env["res.partner"].create(
            {
                "name": "Acsone",
                "street": "Zone industrielle 22",
                "city": "Kehlen",
                "zip": "8287",
                "country_id": cls.luxembourg.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        super(TestResPartner, cls).tearDownClass()

    def test_country_is_belgium(self):
        self.assertTrue(self.partner_be.is_be)

    def test_country_is_not_belgium(self):
        self.assertFalse(self.partner_lu.is_be)
