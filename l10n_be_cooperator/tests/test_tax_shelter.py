# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import SavepointCase

from odoo.addons.cooperator.tests.cooperator_test_mixin import CooperatorTestMixin


class TestTaxShelter(SavepointCase, CooperatorTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_cooperator_test_data()

    def _create_dummy_cooperator_2021(self):
        vals = self.get_dummy_subscription_requests_vals()
        vals["date"] = date(2021, 6, 21)
        subscription_request = self.env["subscription.request"].create(vals)
        subscription_request.validate_subscription_request()
        self.pay_invoice(
            subscription_request.capital_release_request,
            payment_date=date(2021, 6, 22),
        )
        return subscription_request.partner_id

    def _create_tax_shelter_declaration_2022(self):
        declaration = self.env["tax.shelter.declaration"].create(
            {
                "name": "2022",
                "fiscal_year": 2021,
                "date_from": date(2021, 1, 1),
                "date_to": date(2021, 12, 31),
                "month_from": "janvier",
                "month_to": "décembre",
                "tax_shelter_percentage": "45",
                "tax_shelter_capital_limit": 250000,
            }
        )
        declaration.compute_declaration()
        declaration.validate_declaration()
        return declaration

    def test_tax_shelter_certificates(self):
        cooperator = self._create_dummy_cooperator_2021()
        declaration = self._create_tax_shelter_declaration_2022()
        certificates = declaration.tax_shelter_certificates
        self.assertEqual(len(certificates), 1)
        certificate = certificates[0]
        self.assertEqual(certificate.partner_id, cooperator)
        self.assertEqual(certificate.state, "validated")
        self.assertEqual(certificate.total_amount, 50)

    def test_tax_shelter_certificates_mail(self):
        cooperator = self._create_dummy_cooperator_2021()
        declaration = self._create_tax_shelter_declaration_2022()
        self.env["tax.shelter.certificate"].batch_send_tax_shelter_certificate()
        certificates = declaration.tax_shelter_certificates
        self.assertEqual(certificates[0].state, "sent")
        message = self.env["mail.mail"].search([])[0]
        self.assertEqual(message.recipient_ids, cooperator)
        attachments = message.attachment_ids.sorted(key="id")
        self.assertEqual(len(attachments), 2)
        self.assertEqual(
            attachments[0].name,
            "first name last name Tax Shelter Subscription 2022.pdf",
        )
        self.assertEqual(
            attachments[1].name, "first name last name Tax Shelter Shares 2022.pdf"
        )
