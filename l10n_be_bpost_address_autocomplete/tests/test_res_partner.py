import requests

from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()

        cls.partner_be = cls.env["res.partner"].create(
            {
                "name": "Acsone",
            }
        )

    @classmethod
    def tearDownClass(cls):
        super(TestResPartner, cls).tearDownClass()

    def test_country_is_belgium(self):
        self.partner_be.is_belgian_address = True
        self.partner_be._onchange_is_belgian_address()
        self.assertTrue(self.partner_be.country_id == self.env.ref("base.be"))

    def test_country_is_not_belgium(self):
        self.partner_be.is_belgian_address = False
        self.partner_be._onchange_is_belgian_address()
        self.assertFalse(self.partner_be.country_id == self.env.ref("base.be"))

    @mute_logger("py.warnings")
    def test_api_call(self):
        response = requests.get(
            "https://webservices-pub.bpost.be/ws/"
            "ExternalMailingAddressProofingCSREST_v1/address/autocomplete?"
            "id=1&q=watterloo",
            timeout=10,
            verify=False,
        )
        self.assertEqual(response.status_code, 200)
