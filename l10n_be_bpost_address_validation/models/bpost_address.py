# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class BpostAddress:
    def __init__(self, result):
        """Transforms the JSON result into a BpostAddress object"""

        validated_address_result = result["ValidateAddressesResponse"][
            "ValidatedAddressResultList"
        ]["ValidatedAddressResult"][0]
        validated_address = validated_address_result["ValidatedAddressList"][
            "ValidatedAddress"
        ][0]
        postal_address = validated_address["PostalAddress"]
        (
            self.street_number,
            self.street_name,
            self.postal_code,
            self.municipality_name,
            self.latitude,
            self.longitude,
            self.street_number,
            self.error,
        ) = (None, None, None, None, None, None, None, None)

        if (
            "StructuredDeliveryPointLocation" in postal_address
            and "StructuredPostalCodeMunicipality" in postal_address
        ):
            self.street_name = postal_address["StructuredDeliveryPointLocation"][
                "StreetName"
            ]
            self.postal_code = postal_address["StructuredPostalCodeMunicipality"][
                "PostalCode"
            ]
            self.municipality_name = postal_address["StructuredPostalCodeMunicipality"][
                "MunicipalityName"
            ]

            if "ServicePointDetail" in validated_address:
                geographical_location = validated_address["ServicePointDetail"][
                    "GeographicalLocationInfo"
                ]["GeographicalLocation"]
                self.latitude = geographical_location["Latitude"]
                self.longitude = geographical_location["Longitude"]

            if "StreetNumber" in postal_address["StructuredDeliveryPointLocation"]:
                self.street_number = postal_address["StructuredDeliveryPointLocation"][
                    "StreetNumber"
                ]

        if "Error" in validated_address_result:
            self.error = validated_address_result["Error"]

    def toJson(self):
        """Convert the BpostAdress object to JSON"""

        json = {}
        if (
            self.street_name is not None
            and self.postal_code is not None
            and self.municipality_name is not None
            and self.latitude is not None
            and self.longitude is not None
        ):
            json = {
                "street_name": self.street_name,
                "postal_code": self.postal_code,
                "municipality_name": self.municipality_name,
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
            if self.street_number is not None:
                json.update({"street_number": self.street_number})
            if self.error is not None:
                json.update({"error": self.error})
        else:
            json.update({"error": self.error})
        return json
