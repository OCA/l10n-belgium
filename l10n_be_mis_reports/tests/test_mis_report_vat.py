# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMisReportVat(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("be")
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env.ref("l10n_be_mis_reports.mis_report_vat")
        cls.tax_sale_21 = cls.env["account.tax"].search(
            [
                *cls.env["account.tax"]._check_company_domain(cls.env.company),
                ("type_tax_use", "=", "sale"),
                ("amount_type", "=", "percent"),
                ("amount", "=", 21),
            ],
            limit=1,
        )

    def _evaluate(self):
        return self.report.evaluate(
            self.report._prepare_aep(self.env.company),
            "2026-07-01",
            "2026-09-30",
        )

    def test_invoice_and_credit_note(self):
        self.init_invoice(
            "out_invoice",
            invoice_date="2026-08-01",
            amounts=[1000.0],
            taxes=self.tax_sale_21,
            post=True,
        )
        self.init_invoice(
            "out_refund",
            invoice_date="2026-08-15",
            amounts=[100.0],
            taxes=self.tax_sale_21,
            post=True,
        )
        data = self._evaluate()
        self.assertAlmostEqual(data["grid_03"], 1000.0)
        self.assertAlmostEqual(data["grid_54"], 210.0)
        self.assertAlmostEqual(data["grid_49"], 100.0)
        self.assertAlmostEqual(data["grid_64"], 21.0)
        self.assertAlmostEqual(data["grid_71"], 189.0)
