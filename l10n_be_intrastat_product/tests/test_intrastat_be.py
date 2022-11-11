# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase


class TestIntrastatBe(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inv_obj = cls.env["account.move"]
        cls.fpos_obj = cls.env["account.fiscal.position"]
        cls.region_obj = cls.env["intrastat.region"]
        cls.decl_obj = cls.env["l10n.be.intrastat.product.declaration"]

        cls.company = cls.env.company
        cls.env.company.country_id = cls.env.ref("base.be")
        cls.company.intrastat_region_id = cls.env.ref(
            "l10n_be_intrastat_product.intrastat_region_2"
        )
        cls.fpos = cls.fpos_obj.create(
            {
                "name": "Intrastat Fiscal Position",
                "intrastat": True,
                "vat_required": True,
            }
        )
        cls.fpos_na = cls.fpos_obj.create(
            {
                "name": "Intrastat Fiscal Position",
                "intrastat": True,
                "vat_required": False,
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
                "origin_country_id": cls.env.ref("base.be").id,
                "hs_code_id": cls.hs_code_horse.id,
            }
        )
        cls.product_foal = cls.env["product.product"].create(
            {
                "name": "Foal",
                "weight": 230.0,
                "list_price": 2000.0,
                "standard_price": 1200.0,
                "origin_country_id": cls.env.ref("base.be").id,
                "hs_code_id": cls.hs_code_horse.id,
            }
        )
        cls.partner_b2b_1 = cls.env["res.partner"].create(
            {
                "name": "NL B2B 1",
                "country_id": cls.env.ref("base.nl").id,
                "is_company": True,
                "vat": "NL 123456782B90",
                "property_account_position_id": cls.fpos.id,
            }
        )
        cls.partner_b2b_2 = cls.env["res.partner"].create(
            {
                "name": "NL B2B 2",
                "country_id": cls.env.ref("base.nl").id,
                "is_company": True,
                "vat": "NL000000000B00",
                "property_account_position_id": cls.fpos.id,
            }
        )
        cls.partner_b2b_na = cls.env["res.partner"].create(
            {
                "name": "NL B2B NA",
                "country_id": cls.env.ref("base.nl").id,
                "is_company": True,
                "property_account_position_id": cls.fpos_na.id,
            }
        )
        cls.partner_b2c = cls.env["res.partner"].create(
            {
                "name": "NL B2C",
                "country_id": cls.env.ref("base.nl").id,
                "is_company": False,
                "property_account_position_id": cls.fpos.id,
            }
        )

    def test_be_sale_b2b(self):

        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
                "fiscal_position_id": self.fpos.id,
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
        declaration.generate_declaration()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[0].vat, "NL123456782B90")
        self.assertEqual(dlines[0].src_dest_country_code, "NL")

        # handle refund for company with no arrivals declaration
        # TODO: add also return use case but this one is more
        # since it implies creation of SO, with pickings and
        # refund created for pickings.
        # The current implementation is also based upon the
        # OCA stock_picking_invoice_link module which is currently
        # not in the module dependency (we check the presence of
        # this module via hasattr)
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=inv_out.ids)
            .create(
                {
                    "date": inv_out.date,
                    "reason": "test refund",
                    "refund_method": "refund",
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
        declaration.generate_declaration()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[1].amount_company_currency, -5000.0)
        self.assertEqual(dlines[0].amount_company_currency, 0.0)

    def test_be_sale_b2b_na(self):

        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2b_na.id,
                "fiscal_position_id": self.fpos_na.id,
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
        declaration.generate_declaration()
        dlines = declaration.declaration_line_ids
        self.assertEqual(dlines[0].vat, "QV999999999999")

    def test_be_sale_b2c(self):

        inv_out = self.inv_obj.with_context(default_move_type="out_invoice").create(
            {
                "partner_id": self.partner_b2c.id,
                "fiscal_position_id": self.fpos.id,
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
        declaration.generate_declaration()
        # clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(dlines[0].vat, "QV999999999999")

    def test_be_purchase(self):

        inv_in1 = self.inv_obj.with_context(default_move_type="in_invoice").create(
            {
                "partner_id": self.partner_b2b_1.id,
                "fiscal_position_id": self.fpos.id,
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
                "fiscal_position_id": self.fpos.id,
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
        declaration.generate_declaration()
        clines = declaration.computation_line_ids
        dlines = declaration.declaration_line_ids
        self.assertEqual(clines[1].weight, 460.0)
        self.assertEqual(dlines[0].amount_company_currency, 5400.0)
