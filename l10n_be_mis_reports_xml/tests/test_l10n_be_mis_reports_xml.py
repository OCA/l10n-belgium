# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase
from datetime import date


class TestXMLReports(TransactionCase):
    def test_be_vat_declaration_wizard(self):
        # more about coverage than testing
        today = date.today()
        mr_template = self.browse_ref("l10n_be_mis_reports.mis_report_vat")
        mr_instance = self.env["mis.report.instance"].create(
            {
                "name": "Test VAT Report",
                "report_id": mr_template.id,
                "date_from": date(today.year, 1, 1),
                "date_to": date(today.year + 1, 4, 1),
            }
        )
        self.assertTrue(mr_instance._is_be_vat_declaration)

        vat_wizard = (
            self.env["be.vat.declaration.wizard"]
            .with_context({"active_id": mr_instance.id})
            .create(
                {
                    "ask_restitution": True,
                    "period": "quarter",
                }
            )
        )
        self.assertEqual(vat_wizard.period_value, 1)

        vat_wizard.generate_xml()
