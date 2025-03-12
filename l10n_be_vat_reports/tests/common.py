# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml.etree import XML

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestVatReportsCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.ref("l10n_be.demo_company_be")
        cls.env.user.company_id = company
        cls.env.user.company_ids = [Command.set(company.ids)]

    def _create_test_data(self, invoice_tax):
        company = self.env.company
        company.partner_id.write({"vat": "PT999999990"})
        self.partner = self.env["res.partner"].create(
            {
                "name": "dummy customer",
                "vat": "BE0477472701",
            }
        )
        invoice = self._create_test_invoice(invoice_tax)
        invoice.action_post()

    def _create_test_invoice(self, invoice_tax):
        company = self.env.company
        account_line = self.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
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

    def _get_xml_from_report_action(self, report_action):
        report = self.env["ir.actions.report"]._get_report_from_name(
            report_action["report_name"]
        )
        report_result = report._render(
            report, report_action["context"]["active_ids"][0], {}
        )
        return XML(report_result[0])
