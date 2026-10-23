# Copyright 2021 Coop IT Easy SC
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

NS = {
    "v": "http://www.minfin.fgov.be/VATConsignment",
    "c": "http://www.minfin.fgov.be/InputCommon",
}


@tagged("post_install", "-at_install")
class TestXMLReports(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("be")
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.write({"vat": "BE0477472701", "phone": "+32 470 12 34 56"})
        cls.mr_instance = cls.env["mis.report.instance"].create(
            {
                "name": "Test VAT Report",
                "report_id": cls.env.ref("l10n_be_mis_reports.mis_report_vat").id,
                "date_from": date(2026, 7, 1),
                "date_to": date(2026, 9, 30),
                "company_id": cls.env.company.id,
            }
        )

    def test_be_vat_declaration_wizard(self):
        self.assertTrue(self.mr_instance._is_be_vat_declaration)
        vat_wizard = (
            self.env["be.vat.declaration.wizard"]
            .with_context(active_id=self.mr_instance.id)
            .create({"ask_restitution": True, "period": "quarter"})
        )
        self.assertEqual(vat_wizard.period_value, 3)
        self.assertEqual(vat_wizard.declarant_vat, "0477472701")
        self.assertEqual(vat_wizard.declarant_phone, "0032470123456")
        self.assertTrue(vat_wizard.generate_xml())
        report = self.env.ref(
            "l10n_be_mis_reports_xml.l10n_be_vat_declaration_xml_report"
        )
        xml, _format = self.env["ir.actions.report"]._render(
            report.report_name, vat_wizard.ids
        )
        root = etree.fromstring(xml)
        declaration = root.find("v:VATDeclaration", NS)
        self.assertEqual(
            declaration.findtext("v:Declarant/c:VATNumber", namespaces=NS),
            "0477472701",
        )
        self.assertEqual(declaration.findtext("v:Period/v:Quarter", namespaces=NS), "3")
        self.assertEqual(declaration.findtext("v:Period/v:Year", namespaces=NS), "2026")
        self.assertEqual(declaration.find("v:Ask", NS).get("Restitution"), "YES")

    def test_generate_xml_requires_company_vat(self):
        self.env.company.vat = False
        vat_wizard = (
            self.env["be.vat.declaration.wizard"]
            .with_context(active_id=self.mr_instance.id)
            .create({"period": "quarter"})
        )
        with self.assertRaises(UserError):
            vat_wizard.generate_xml()
