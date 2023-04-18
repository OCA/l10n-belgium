import responses

from odoo.tests.common import TransactionCase


class TestBpostAddressValidationWizard(TransactionCase):
    @classmethod
    @responses.activate
    def setUpClass(cls):
        super(TestBpostAddressValidationWizard, cls).setUpClass()

        cls.country = cls.env["res.country"].search([("code", "=", "BE")])
        cls.luxembourg = cls.env["res.country"].search([("code", "=", "LU")])
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Acsone",
                "street": "Quai Banneng 6",
                "city": "Liège",
                "zip": "4000",
                "country_id": cls.country.id,
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
        cls.return_value = {
            "ValidateAddressesResponse": {
                "ValidatedAddressResultList": {
                    "ValidatedAddressResult": [
                        {
                            "@id": "1",
                            "ValidatedAddressList": {
                                "ValidatedAddress": [
                                    {
                                        "PostalAddress": {
                                            "StructuredDeliveryPointLocation": {
                                                "StreetName": "QUAI BANNING",
                                                "StreetNumber": "6",
                                            },
                                            "StructuredPostalCodeMunicipality": {
                                                "PostalCode": "4000",
                                                "MunicipalityName": "LIÈGE",
                                            },
                                            "CountryName": "BELGIQUE",
                                        },
                                        "AddressLanguage": "fr",
                                        "ServicePointDetail": {
                                            "GeographicalLocationInfo": {
                                                "GeographicalLocation": {
                                                    "Latitude": {
                                                        "Value": "50.61389",
                                                        "CoordinateType": "DEGDEC",
                                                    },
                                                    "Longitude": {
                                                        "Value": "5.575775",
                                                        "CoordinateType": "DEGDEC",
                                                    },
                                                }
                                            }
                                        },
                                        "Label": {
                                            "Line": ["QUAI BANNING 6", "4000 LIÈGE"]
                                        },
                                    }
                                ]
                            },
                            "Error": [
                                {
                                    "ComponentRef": "UnstructuredDeliveryPointLocation",
                                    "ErrorCode": "anomaly_in_field",
                                    "ErrorSeverity": "warning",
                                }
                            ],
                            "DetectedInputAddressLanguage": "fr",
                            "FormattedSubmittedAddress": {
                                "Line": ["Quai Banneng 6", "4000 Liège"]
                            },
                            "TransactionID": "10379d53-2072-420e-b875-e83148ef94e0",
                        }
                    ]
                }
            }
        }
        responses.add(
            method=responses.POST,
            url="https://webservices-pub.bpost.be/ws/"
            + "ExternalMailingAddressProofingCSREST_v1/address/validateAddresses",
            json=cls.return_value,
        )
        cls.wizard = cls.env["bpost.address.validation.wizard"].create(
            {"partner_id": cls.partner.id}
        )
        cls.wizard._compute_response_address()

    @classmethod
    def tearDownClass(cls):
        super(TestBpostAddressValidationWizard, cls).tearDownClass()

    def test_is_not_valid(self):
        self.assertFalse(self.wizard.is_valid)

    def test_apply_changes(self):
        self.wizard.apply_changes()

        self.assertEqual("QUAI BANNING 6", self.partner.street)
        self.assertEqual("LIÈGE", self.partner.city)
        self.assertEqual("4000", self.partner.zip)

    def test_suggest_changes(self):
        self.assertEqual("QUAI BANNING 6 4000, LIÈGE", self.wizard.suggest_changes)
        self.assertFalse(self.wizard.bad_address)
        self.assertFalse(self.wizard.is_valid)

    def test_invalid_address(self):
        self.partner.street = "Quai Banning"
        self.wizard._compute_response_address()
        self.assertTrue(self.wizard.bad_address)
        self.assertFalse(self.wizard.is_valid)

    def test_valid_address(self):
        self.partner.street = "Quai Banning 6"
        self.wizard._compute_response_address()
        self.assertTrue(self.wizard.is_valid)
        self.assertFalse(self.wizard.bad_address)

    def test_partner_from_another_country(self):
        wizard = self.env["bpost.address.validation.wizard"].create(
            {"partner_id": self.partner_lu.id}
        )
        wizard._compute_response_address()
        self.assertTrue(wizard.is_valid)
        self.assertFalse(wizard.bad_address)

    def test_invalid_address_and_apply_changes(self):
        self.partner.street = "Quai Banning"
        self.wizard._compute_response_address()
        self.wizard.apply_changes()
        self.assertTrue(self.wizard.bad_address)
        self.assertFalse(self.wizard.is_valid)
        self.assertEqual(
            "The given address is not complete or the address cannot be found",
            self.wizard.warning_message,
        )

        self.assertNotEqual("QUAI BANNING", self.partner.street)
        self.assertNotEqual("LIÈGE", self.partner.city)

    def test_address_not_found(self):
        self.partner.street = "benneng"
        self.wizard._compute_response_address()
        self.assertTrue(self.wizard.bad_address)
        self.assertFalse(self.wizard.is_valid)
