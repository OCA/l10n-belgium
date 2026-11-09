# Copyright 2026 Omnifloo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.mis_builder.models.data_error import DataError

DATE_FROM = "2026-01-01"
DATE_TO = "2026-12-31"


@tagged("post_install", "-at_install")
class TestL10nBeMisReports(AccountTestInvoicingCommon):
    """Evaluate the Belgian MIS templates on a company using the l10n_be chart."""

    @classmethod
    @AccountTestInvoicingCommon.setup_country("be")
    def setUpClass(cls):
        super().setUpClass()
        tax_21 = cls.env["account.chart.template"].ref("attn_VAT-OUT-21-L")
        cls.invoice = cls._create_invoice_one_line(
            price_unit=1000.0,
            tax_ids=tax_21,
            partner_id=cls.partner_a,
            invoice_date="2026-03-15",
            post=True,
        )
        cls.reports = cls.env["ir.model.data"].search(
            [("module", "=", "l10n_be_mis_reports"), ("model", "=", "mis.report")]
        )

    def _evaluate(self, xmlid):
        report = self.env.ref(f"l10n_be_mis_reports.{xmlid}")
        aep = report._prepare_aep(self.env.company)
        return report.evaluate(aep, date_from=DATE_FROM, date_to=DATE_TO)

    def test_invoice_posted_on_be_accounts(self):
        self.assertEqual(self.invoice.state, "posted")
        codes = set(self.invoice.line_ids.account_id.mapped("code"))
        self.assertTrue(any(code.startswith("70") for code in codes), codes)
        self.assertTrue(any(code.startswith("40") for code in codes), codes)

    def test_all_templates_evaluate_without_error(self):
        # 21 templates: 9 models x (balance sheet + P&L), 2 deprecated, VAT
        self.assertEqual(len(self.reports), 21)
        for imd in self.reports:
            report = self.env["mis.report"].browse(imd.res_id)
            aep = report._prepare_aep(self.env.company)
            values = report.evaluate(aep, date_from=DATE_FROM, date_to=DATE_TO)
            errors = {
                name: value
                for name, value in values.items()
                if isinstance(value, DataError)
            }
            self.assertFalse(errors, f"{imd.name}: {errors}")

    def test_profit_and_loss_abridged(self):
        values = self._evaluate("new_mis_report_pl_m02_f")
        self.assertAlmostEqual(values["rub_70"], 1000.0)
        self.assertAlmostEqual(values["rub_9904"], 1000.0)

    def test_balance_sheet_abridged(self):
        values = self._evaluate("new_mis_report_bs_m02_f")
        self.assertAlmostEqual(values["rub_20_58"], 1210.0)
