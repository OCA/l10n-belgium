# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import Mock

from odoo.exceptions import RedirectWarning, UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestIntrastatBe(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        be = cls.env.ref("base.be")
        nl = cls.env.ref("base.nl")
        europe = cls.env.ref("base.europe")

        cls.inv_obj = cls.env["account.move"]
        cls.fpos_obj = cls.env["account.fiscal.position"]
        cls.region_obj = cls.env["intrastat.region"]
        cls.decl_obj = cls.env["intrastat.product.declaration"]

        cls.company = cls.env.company
        cls.company.partner_id.update(
            {
                "company_registry": "0820512013",
                "vat": "BE0820512013",
                "country_id": be.id,
            }
        )
        cls.company.update(
            {
                "account_fiscal_country_id": be.id,
                "intrastat_region_id": cls.env.ref(
                    "l10n_be_intrastat_product.intrastat_region_2"
                ).id,
                "incoterm_id": cls.env.ref("account.incoterm_FOB").id,
            }
        )
        cls.fpos_b2b = cls.fpos_obj.create(
            {
                "name": "Intrastat Fiscal Position (B2B)",
                "intrastat": "b2b",
                "vat_required": True,
                "country_id": be.id,
                "country_group_id": europe.id,
            }
        )
        cls.fpos_b2c = cls.fpos_obj.create(
            {
                "name": "Intrastat Fiscal Position (B2C)",
                "intrastat": "b2c",
                "vat_required": False,
                "country_id": be.id,
                "country_group_id": europe.id,
            }
        )
        cls.hs_code_cn = cls.env["hs.code"].create(
            {
                "description": "Rough discount, credit notes",
                "local_code": "99600000",
                "intrastat_unit_id": cls.env.ref(
                    "intrastat_product.intrastat_unit_pce"
                ).id,
            }
        )
        cls.hs_code_horse = cls.env["hs.code"].create(
            {
                "description": "Horse",
                "local_code": "01012100",
                "intrastat_unit_id": cls.env.ref(
                    "intrastat_product.intrastat_unit_pce"
                ).id,
            }
        )
        cls.product_horse = cls.env["product.product"].create(
            {
                "name": "Horse",
                "weight": 500.0,
                "list_price": 5000.0,
                "standard_price": 3000.0,
                "origin_country_id": be.id,
                "hs_code_id": cls.hs_code_horse.id,
            }
        )
        cls.product_foal = cls.env["product.product"].create(
            {
                "name": "Foal",
                "weight": 230.0,
                "list_price": 2000.0,
                "standard_price": 1200.0,
                "origin_country_id": be.id,
                "hs_code_id": cls.hs_code_horse.id,
            }
        )
        cls.partner_b2b_1 = cls.env["res.partner"].create(
            {
                "name": "NL B2B 1",
                "country_id": nl.id,
                "is_company": True,
                "vat": "NL 123456782B90",
                "property_account_position_id": cls.fpos_b2b.id,
            }
        )
        cls.partner_b2b_2 = cls.env["res.partner"].create(
            {
                "name": "NL B2B 2",
                "country_id": nl.id,
                "is_company": True,
                "vat": "NL000000012B01",
                "property_account_position_id": cls.fpos_b2b.id,
            }
        )
        cls.partner_b2b_na = (
            cls.env["res.partner"]
            .with_context(no_vat_validation=True)
            .create(
                {
                    "name": "NL B2B NA",
                    "country_id": nl.id,
                    "is_company": True,
                    "vat": "na",
                    "property_account_position_id": cls.fpos_b2b.id,
                }
            )
        )
        cls.partner_b2c = cls.env["res.partner"].create(
            {
                "name": "NL B2C",
                "country_id": nl.id,
                "is_company": False,
                "property_account_position_id": cls.fpos_b2c.id,
            }
        )
        taxes = cls.env["account.tax"].search([("company_id", "=", cls.company.id)])
        taxes.mapped("tax_group_id").update({"country_id": be.id})
        taxes.update({"country_id": be.id})
        cls.taxes = taxes

    def test_be_sale_b2b(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.confirmed2done()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[0].vat, "NL123456782B90")
        self.assertEqual(dlines[0].src_dest_country_code, "NL")

        # handle refund for company with no arrivals declaration
        # TODO: add also return use case but this one is more work
        # since it implies creation of SO, with pickings and
        # refund created for pickings.
        # The current implementation is also based upon the
        # OCA stock_picking_invoice_link module which is currently
        # not in the module dependency (we check the presence of
        # this module via hasattr)
        sale_journal_rec = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv_out.ids)
            .create(
                {
                    "date": inv_out.date,
                    "reason": "test refund",
                    "journal_id": sale_journal_rec.id,
                }
            )
            .reverse_moves()
        )
        refund = self.env["account.move"].browse(reversal["res_id"])
        refund.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.confirmed2done()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[1].amount_company_currency, -5000.0)
        self.assertEqual(dlines[0].amount_company_currency, 0.0)

    def test_be_sale_b2b_na(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_na.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.confirmed2done()
        dlines = declaration.declaration_line_ids
        self.assertEqual(dlines[0].vat, "QV999999999999")

    def test_be_sale_b2c(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2c.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.confirmed2done()
        # clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(dlines[0].vat, "QV999999999999")

    def test_be_purchase(self):
        inv_in1 = self.inv_obj.with_context(default_move_type="in_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_in1) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_in1.invoice_date = inv_in1.date
        inv_in1.action_post()

        inv_in2 = self.inv_obj.with_context(default_move_type="in_invoice").create(
            {
                "partner_id": self.partner_b2b_2.id,
            }
        )
        with Form(inv_in2) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_foal
                ail.quantity = 2.0
        inv_in2.invoice_date = inv_in2.date
        inv_in2.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "arrivals",
                "company_id": self.env.company.id,
                "year": str(inv_in1.date.year),
                "month": str(inv_in1.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.confirmed2done()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[1].weight, 460.0)
        self.assertEqual(dlines[0].amount_company_currency, 5400.0)

    def test_be_region_not_configured(self):
        self.company.intrastat_region_id = False
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        with self.assertRaisesRegex(RedirectWarning, "Intrastat Region"):
            declaration.action_gather()

    def test_be_refund_transaction_already_set(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        sale_journal_rec = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv_out.ids)
            .create(
                {
                    "date": inv_out.date,
                    "reason": "test refund with transaction code",
                    "journal_id": sale_journal_rec.id,
                }
            )
            .reverse_moves()
        )
        refund = self.env["account.move"].browse(reversal["res_id"])
        refund.intrastat_transaction_id = self.env.ref(
            "intrastat_product.intrastat_transaction_31"
        ).id
        refund.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        clines = declaration.computation_line_ids
        self.assertEqual(
            clines[1].transaction_id,
            self.env.ref("intrastat_product.intrastat_transaction_31"),
        )

    def test_be_refund_outside_period_warning(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
                "invoice_date": "2025-01-15",
                "date": "2025-01-15",
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        sale_journal_rec = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        refund_date = "2025-03-15"
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv_out.ids)
            .create(
                {
                    "date": refund_date,
                    "reason": "test refund outside period",
                    "journal_id": sale_journal_rec.id,
                }
            )
            .reverse_moves()
        )
        refund = self.env["account.move"].browse(reversal["res_id"])
        refund.invoice_date = refund_date
        refund.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": "2025",
                "month": "03",
            }
        )
        declaration.action_gather()
        self.assertIn("Unable to determine the correct handling", declaration.note)

    def test_be_reporting_level_standard(self):
        self.company.intrastat_dispatches = "standard"
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        self.assertEqual(declaration.reporting_level, "standard")
        declaration.confirmed2done()
        self.assertTrue(declaration.xml_attachment_id)

    def test_be_node_item_missing_field(self):
        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
            }
        )
        with Form(inv_out) as inv_form:
            with inv_form.invoice_line_ids.new() as ail:
                ail.product_id = self.product_horse
        inv_out.action_post()

        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.env.company.id,
                "year": str(inv_out.date.year),
                "month": str(inv_out.date.month).zfill(2),
            }
        )
        declaration.action_gather()
        declaration.draft2confirmed()
        declaration.declaration_line_ids.transaction_id = False
        with self.assertRaisesRegex(UserError, "Missing"):
            declaration.confirmed2done()

    def _make_refund_mock(self, move_type):
        """A refund with a linked picking, faked via a Mock since the real
        picking_ids field is only added by the optional OCA
        stock_picking_invoice_link module (not a dependency here)."""
        return Mock(
            intrastat_transaction_id=False,
            picking_ids=Mock(),
            move_type=move_type,
            src_dest_region_id=self.env.ref(
                "l10n_be_intrastat_product.intrastat_region_2"
            ),
        )

    def _prepare_refund_notedict(self, declaration):
        notedict, _key2label = declaration._prepare_notedict()
        declaration._gather_invoices_init(notedict)
        return notedict

    def test_be_refund_with_picking_in_arrivals_exempt(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "arrivals",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        self.company.intrastat_dispatches = "exempt"
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("in_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(
            line_vals["hs_code_id"], notedict["credit_note_code_origin"].id
        )
        self.assertEqual(
            line_vals["region_id"],
            self.env.ref("l10n_be_intrastat_product.intrastat_region_2").id,
        )
        self.assertFalse(line_vals["transaction_id"])

    def test_be_refund_with_picking_in_arrivals_not_exempt(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "arrivals",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        self.company.intrastat_dispatches = "extended"
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("in_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(line_vals, {})

    def test_be_refund_with_picking_in_dispatches(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("in_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(
            line_vals["transaction_id"], notedict["transcation_21_origin"].id
        )
        self.assertEqual(
            line_vals["region_id"],
            self.env.ref("l10n_be_intrastat_product.intrastat_region_2").id,
        )

    def test_be_refund_with_picking_out_dispatches_exempt(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        self.company.intrastat_arrivals = "exempt"
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("out_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(
            line_vals["hs_code_id"], notedict["credit_note_code_origin"].id
        )
        self.assertFalse(line_vals["transaction_id"])

    def test_be_refund_with_picking_out_dispatches_not_exempt(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        self.company.intrastat_arrivals = "extended"
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("out_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(line_vals, {})

    def test_be_refund_with_picking_out_arrivals(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "arrivals",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        notedict = self._prepare_refund_notedict(declaration)
        inv_line = Mock(move_id=self._make_refund_mock("out_refund"))
        line_vals = {
            "weight": 10.0,
            "suppl_unit_qty": 1,
            "amount_company_currency": 100.0,
        }
        declaration._handle_refund(inv_line, line_vals, notedict)
        self.assertEqual(
            line_vals["transaction_id"], notedict["transcation_21_origin"].id
        )
        self.assertEqual(
            line_vals["region_id"],
            self.env.ref("l10n_be_intrastat_product.intrastat_region_2").id,
        )

    def test_be_generate_xml_non_be_company(self):
        nl_company = self.env["res.company"].create(
            {
                "name": "NL Test Company",
                "country_id": self.env.ref("base.nl").id,
            }
        )
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": nl_company.id,
                "year": "2025",
                "month": "01",
            }
        )
        self.assertFalse(declaration._generate_xml())

    def test_be_xls_computation_line_fields(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        res = declaration._xls_computation_line_fields()
        self.assertNotIn("product_origin_country", res)

    def test_be_xls_declaration_line_fields_dispatches(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "dispatches",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        res = declaration._xls_declaration_line_fields()
        i = res.index("hs_code")
        self.assertEqual(res[i + 1], "product_origin_country")

    def test_be_xls_declaration_line_fields_arrivals(self):
        declaration = self.decl_obj.create(
            {
                "declaration_type": "arrivals",
                "company_id": self.company.id,
                "year": "2025",
                "month": "01",
            }
        )
        res = declaration._xls_declaration_line_fields()
        self.assertNotIn("product_origin_country", res)
