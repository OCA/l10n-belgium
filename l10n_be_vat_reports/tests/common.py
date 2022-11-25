# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestVatReportsCommon(TransactionCase):
    def _create_test_data(self, invoice_tax):
        chart = self.env.ref("l10n_be.l10nbe_chart_template")
        chart.try_loading()
        company = self.env.company
        company.partner_id.write({"vat": "PT999999990"})
        self.partner = self.env["res.partner"].create(
            {
                "name": "dummy customer",
                "vat": "BE0477472701",
            }
        )
        account_rev_type = self.env.ref("account.data_account_type_revenue")
        account_line = self.env["account.account"].search(
            [
                ("user_type_id", "=", account_rev_type.id),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        invoice = self.env["account.move"].create(
            {
                "type": "out_invoice",
                "company_id": company.id,
                "currency_id": self.env.ref("base.EUR").id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Computer SC234",
                            "price_unit": 450.0,
                            "quantity": 1.0,
                            "product_id": self.env.ref("product.product_product_3").id,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "tax_ids": [(6, 0, [invoice_tax.id])],
                            "account_id": account_line.id,
                        },
                    )
                ],
                "partner_id": self.partner.id,
            }
        )
        invoice.action_post()
