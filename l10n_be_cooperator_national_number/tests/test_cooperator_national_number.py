# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

from odoo.addons.cooperator.tests.cooperator_test_mixin import CooperatorTestMixin


class TestCooperatorNationalNumber(SavepointCase, CooperatorTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_cooperator_test_data()

    def test_national_number_applied_to_partner(self):
        id_number = 12345
        self.subscription_request_1.national_number = id_number
        self.subscription_request_1.validate_subscription_request()
        partner = self.subscription_request_1.partner_id
        created_id_number = self.env["res.partner.id_number"].search(
            [('name', '=', id_number)])
        self.assertTrue(created_id_number)
        self.assertEqual(created_id_number.partner_id, partner)

    # def test_error_if_company(self):
        # vals = self.get_dummy_subscription_requests_vals()
        # subscription_request = self.env["subscription.request"].create(vals)
        # id_number = 12345
        # self.subscription_request_1.national_number = id_number
        # with self.assertRaises(UserError):
        #     self.subscription_request_1.validate_subscription_request()

    def test_error_if_nrn_required(self):
        with self.assertRaises(UserError):
            self.subscription_request_1.validate_subscription_request()
