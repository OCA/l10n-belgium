# Copyright 2021 Coop IT Easy SC
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

VAT_CONSIGNMENT_NS = "http://www.minfin.fgov.be/VATConsignment"
INPUT_COMMON_NS = "http://www.minfin.fgov.be/InputCommon"


class TestXMLReports(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mr_template = cls.env.ref("l10n_be_mis_reports.mis_report_vat")
        cls.company = cls.env.company
        cls.company.write({"vat": "BE0246697724"})
        # Odoo 19's report_action() redirects to the document-layout configurator
        # when the company has no external report layout. Set it so generate_xml()
        # returns the report action itself.
        cls.company.external_report_layout_id = cls.env.ref(
            "web.external_layout_standard"
        ).id

    def _create_instance(self, date_from=None, date_to=None):
        return self.env["mis.report.instance"].create(
            {
                "name": "Test VAT Report",
                "report_id": self.mr_template.id,
                "date_from": date_from or date(2026, 1, 1),
                "date_to": date_to or date(2026, 3, 31),
                "company_id": self.company.id,
            }
        )

    def _create_wizard(self, instance, **values):
        return (
            self.env["be.vat.declaration.wizard"]
            .with_context(active_id=instance.id)
            .create(values)
        )

    def test_is_be_vat_declaration(self):
        instance = self._create_instance()
        self.assertTrue(instance._is_be_vat_declaration)

        other_template = self.env.ref("l10n_be_mis_reports.new_mis_report_pl_m01_f")
        other = self.env["mis.report.instance"].create(
            {
                "name": "Test P&L Report",
                "report_id": other_template.id,
                "date_from": date(2026, 1, 1),
                "date_to": date(2026, 12, 31),
                "company_id": self.company.id,
            }
        )
        self.assertFalse(other._is_be_vat_declaration)

    def test_period_value_month(self):
        instance = self._create_instance(date_from=date(2026, 5, 1))
        wizard = self._create_wizard(instance, period="month")
        self.assertEqual(wizard.period_value, 5)

    def test_period_value_quarter(self):
        instance = self._create_instance(date_from=date(2026, 5, 1))
        wizard = self._create_wizard(instance, period="quarter")
        self.assertEqual(wizard.period_value, 2)

    def test_declarant_vat_strips_formatting(self):
        instance = self._create_instance()
        wizard = self._create_wizard(instance)
        self.assertEqual(wizard.declarant_vat, "0246697724")

    def test_generate_xml_requires_company_vat(self):
        self.company.write({"vat": False})
        instance = self._create_instance()
        wizard = self._create_wizard(instance)
        with self.assertRaises(UserError):
            wizard.generate_xml()

    def test_generate_xml(self):
        instance = self._create_instance()
        wizard = self._create_wizard(instance)
        action = wizard.generate_xml()
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(
            action["report_name"],
            "l10n_be_mis_reports_xml.l10n_be_vat_declaration_xml_template",
        )
        self.assertEqual(action["report_type"], "qweb-xml")

    def test_prepare_xml_data_is_serialisable(self):
        instance = self._create_instance()
        wizard = self._create_wizard(instance)
        xml_data = wizard.prepare_xml_data()
        self.assertIsInstance(xml_data, dict)
        for key, value in xml_data.items():
            self.assertTrue(key.startswith("grid_"))
            self.assertRegex(value, r"^-?\d+\.\d{2}$")

    def test_render_xml_report(self):
        instance = self._create_instance(date_from=date(2026, 1, 1))
        wizard = self._create_wizard(instance, period="month")
        content, report_type = self.env["ir.actions.report"]._render(
            "l10n_be_mis_reports_xml.l10n_be_vat_declaration_xml_report",
            wizard.ids,
        )
        self.assertEqual(report_type, "xml")
        root = etree.fromstring(content)
        self.assertEqual(root.tag, f"{{{VAT_CONSIGNMENT_NS}}}VATConsignment")
        declaration = root.find(f"{{{VAT_CONSIGNMENT_NS}}}VATDeclaration")
        self.assertIsNotNone(declaration)
        declarant_vat = declaration.find(
            f"{{{VAT_CONSIGNMENT_NS}}}Declarant/{{{INPUT_COMMON_NS}}}VATNumber"
        )
        self.assertEqual(declarant_vat.text, "0246697724")
        period = declaration.find(f"{{{VAT_CONSIGNMENT_NS}}}Period")
        self.assertEqual(
            period.find(f"{{{VAT_CONSIGNMENT_NS}}}Month").text,
            "1",
        )
        self.assertEqual(
            period.find(f"{{{VAT_CONSIGNMENT_NS}}}Year").text,
            "2026",
        )
