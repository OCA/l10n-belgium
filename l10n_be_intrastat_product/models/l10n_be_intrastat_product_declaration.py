# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning, UserError

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)

_render = ReportXlsxAbstract._render
_logger = logging.getLogger(__name__)

_INTRASTAT_XMLNS = "http://www.onegate.eu/2010-01-01"


class L10nBeIntrastatProductDeclaration(models.Model):
    _name = "l10n.be.intrastat.product.declaration"
    _description = "Intrastat Product Declaration for Belgium"
    _inherit = ["intrastat.product.declaration", "mail.thread"]

    computation_line_ids = fields.One2many(
        "l10n.be.intrastat.product.computation.line",
        "parent_id",
        string="Intrastat Product Computation Lines",
        states={"done": [("readonly", True)]},
    )
    declaration_line_ids = fields.One2many(
        "l10n.be.intrastat.product.declaration.line",
        "parent_id",
        string="Intrastat Product Declaration Lines",
        states={"done": [("readonly", True)]},
    )

    def _get_intrastat_transaction(self, inv_line, notedict):
        transaction = super()._get_intrastat_transaction(inv_line, notedict)
        msg1 = _("Select a 1 digit intrastat transaction code.")
        msg2 = _("Select a 2 digit intrastat transaction code.")
        module = __name__.split("addons.")[1].split(".")[0]
        if transaction:
            if int(transaction.code) >= 10 and self.year <= "2021":
                self._format_line_note(inv_line, notedict, [msg1])
            elif int(transaction.code) < 10 and self.year > "2021":
                self._format_line_note(inv_line, notedict, [msg2])
        else:
            if self.year <= "2021":
                transaction = self.env.ref("%s.intrastat_transaction_1" % module)
            else:
                transaction = self.env.ref("%s.intrastat_transaction_11" % module)
        invoice = inv_line.move_id
        if not invoice.intrastat_transaction_id:
            cp = invoice.commercial_partner_id
            if not cp.is_company:
                transaction = self.env.ref("%s.intrastat_transaction_12" % module)
        return transaction

    def _get_region(self, inv_line, notedict):
        region = super()._get_region(inv_line, notedict)
        if not region:
            msg = _(
                "The Intrastat Region of the Company is not set, "
                "please configure it first."
            )
            self._account_config_warning(msg)
        return region

    def _get_vat(self, inv_line, notedict):
        inv = inv_line.move_id
        cp = inv.commercial_partner_id
        b2c = not cp.is_company
        b2b_na = cp.is_company and (
            (cp.vat or "").lower().strip() == "na"
            or (not cp.vat and not inv.fiscal_position_id.vat_required)
        )
        if b2c or b2b_na:
            return "QV999999999999"
        else:
            return super()._get_vat(inv_line, notedict)

    def _handle_refund(self, inv_line, line_vals, notedict):
        """
        NBB/BNB Intrastat Manual 2022 :
        - FR : Traiter des notes de crédit p 34
        - NL : Creditnota’s verwerken p 36

        To follow the logic explained in the intrastat manual
        requires a well enforced set of business processes
        to ensure correct encoding of Credit Notes.
        If the transaction code is not set on the Credit Note
        and there is no linked shipment than we fall back to the
        default settings for refunds.

        ŦODO:
        Move the refund handling to the 'intrastat_product' module and
        add refund unit tests.
        """
        refund = inv_line.move_id
        if refund.intrastat_transaction_id:
            line_vals["transaction_id"] = refund.intrastat_transaction_id.id
            return
        # The invoice.picking_ids field in implemented in the
        # OCA stock_picking_invoice_link module
        if hasattr(refund, "picking_ids"):
            return_picking = refund.picking_ids
        else:
            return_picking = False

        if return_picking:

            if refund.move_type == "in_refund":
                if self.declaration_type == "arrivals":
                    if self.company_id.intrastat_dispatches == "exempt":
                        line_vals.update(
                            {
                                "hs_code_id": notedict["credit_note_code"].id,
                                "region_id": refund.src_dest_region_id.id,
                                "transaction_id": False,
                            }
                        )
                    else:
                        line_vals.clear()
                else:
                    line_vals.update(
                        {
                            "region_id": refund.src_dest_region_id.id,
                            "transaction_id": notedict["transcation_21"].id,
                        }
                    )

            else:  # 'out_refund':
                if self.declaration_type == "dispatches":
                    if self.company_id.intrastat_arrivals == "exempt":
                        line_vals.update(
                            {
                                "hs_code_id": notedict["credit_note_code"].id,
                                "region_id": refund.src_dest_region_id.id,
                                "transaction_id": False,
                            }
                        )
                    else:
                        line_vals.clear()
                else:
                    line_vals.update(
                        {
                            "region_id": refund.src_dest_region_id.id,
                            "transaction_id": notedict["transcation_21"].id,
                        }
                    )
        else:  # return_picking is False
            # We assume that there is no movement of goods.
            # This assumption could be wrong but can only be fixed by adjusting the
            # business processes of the company subject to the intrastat declaration.

            start_date = date(int(self.year), int(self.month), 1)
            end_date = start_date + relativedelta(day=1, months=+1, days=-1)
            invoice = refund.reversed_entry_id

            if invoice.state == "posted" and start_date <= invoice.date <= end_date:
                # Manual correction of the declaration lines can be required
                # when the sum of the computation lines results in
                # negative values
                line_vals.update(
                    {
                        "weight": -line_vals["weight"],
                        "suppl_unit_qty": -line_vals["suppl_unit_qty"],
                        "amount_company_currency": -line_vals[
                            "amount_company_currency"
                        ],
                    }
                )
                return

            line_notes = [
                _("Unable to determine the correct handling of Refund."),
                _("Please check/set the Intrastat Transaction Code on the Refund."),
            ]
            self._format_line_note(inv_line, notedict, line_notes)

    def _update_computation_line_vals(self, inv_line, line_vals, notedict):
        super()._update_computation_line_vals(inv_line, line_vals, notedict)
        # handling of refunds
        inv = inv_line.move_id
        if inv.move_type in ["in_refund", "out_refund"]:
            self._handle_refund(inv_line, line_vals, notedict)

        if line_vals:
            if self.declaration_type == "dispatches":
                if not line_vals["vat"]:
                    line_notes = [
                        _("Missing VAT Number on partner '%s'")
                        % inv.partner_id.name_get()[0][1]
                    ]
                    self._format_line_note(inv_line, notedict, line_notes)
            # extended declaration
            if self.reporting_level == "extended":
                incoterm = self._get_incoterm(inv_line, notedict)
                line_vals.update({"incoterm_id": incoterm.id})

    def _handle_invoice_accessory_cost(
        self,
        invoice,
        lines_current_invoice,
        total_inv_accessory_costs_cc,
        total_inv_product_cc,
        total_inv_weight,
    ):
        """
        In Belgium accessory cost should not be added. cf. Intrastat guide 2020
        NBB/BNB (intrastat_manual_basis_en.pdf, ISSN 1782-5482).
        If transport and insurance costs are included in the price of the goods,
        you do not have to make any additional calculation or estimate in
        order to deduct them. However, if they are separately known (e.g.
        stated on a separate line on the invoice), transport and insurance
        costs may not be included in the value of the goods.
        """

    def _gather_invoices_init(self, notedict):
        if self.company_id.country_id.code not in ("be", "BE"):
            raise UserError(
                _(
                    "The Belgian Intrastat Declaration requires "
                    "the Company's Country to be equal to 'Belgium'."
                )
            )

        module = __name__.split("addons.")[1].split(".")[0]

        # Special commodity codes
        # Current version implements only regular credit notes
        special_code = "99600000"
        hs_code = self.env["hs.code"].search([("local_code", "=", special_code)])
        if len(hs_code) > 1:
            hs_code = hs_code.filtered(
                lambda r: r.company_id == self.company_id
            ) or hs_code.filtered(lambda r: not r.company_id)
        if not hs_code:
            action = self.env.ref("%s.intrastat_installer_action" % module)
            msg = (
                _(
                    "Intrastat Code '%s' not found. "
                    "\nYou can update your codes "
                    "via the Intrastat Configuration Wizard."
                )
                % special_code
            )
            raise RedirectWarning(
                msg, action.id, _("Go to the Intrastat Configuration Wizard.")
            )
        notedict["credit_note_code"] = hs_code[0]

        if self.year <= "2021":
            notedict["transcation_21"] = self.env.ref(
                "%s.intrastat_transaction_2" % module
            )
        else:
            notedict["transcation_21"] = self.env.ref(
                "%s.intrastat_transaction_21" % module
            )

    def _prepare_invoice_domain(self):
        """
        Domain should be based on fiscal position in stead of country.
        Both in_ and out_refund must be included in order to cover
        - credit notes with and without return
        - companies subject to arrivals or dispatches only
        """
        domain = super()._prepare_invoice_domain()
        if self.declaration_type == "arrivals":
            domain.append(
                ("move_type", "in", ("in_invoice", "in_refund", "out_refund"))
            )
        elif self.declaration_type == "dispatches":
            domain.append(
                ("move_type", "in", ("out_invoice", "in_refund", "out_refund"))
            )
        return domain

    def _sanitize_vat(self, vat):
        return vat and vat.replace(" ", "").replace(".", "").upper()

    @api.model
    def _group_line_hashcode_fields(self, computation_line):
        res = super()._group_line_hashcode_fields(computation_line)
        if self.declaration_type == "arrivals":
            del res["product_origin_country"]
            del res["vat"]
        if self.reporting_level == "extended":
            res["incoterm"] = computation_line.incoterm_id.id or False
        return res

    @api.model
    def _prepare_grouped_fields(self, computation_line, fields_to_sum):
        vals = super()._prepare_grouped_fields(computation_line, fields_to_sum)
        if self.reporting_level == "extended":
            vals["incoterm_id"] = computation_line.incoterm_id.id
        return vals

    def _check_generate_xml(self):
        self.ensure_one()
        res = super()._check_generate_xml()
        if not self.declaration_line_ids:
            res = self.generate_declaration()
        return res

    def _get_kbo_bce_nr(self):
        kbo_bce_nr = False
        vat = self._sanitize_vat(self.company_id.partner_id.vat)
        if vat and vat[:2] == "BE":
            kbo_bce_nr = vat[2:]
        return kbo_bce_nr

    def _node_Administration(self, parent):
        Administration = etree.SubElement(parent, "Administration")
        From = etree.SubElement(Administration, "From")
        From.text = self._get_kbo_bce_nr()
        From.set("declarerType", "KBO")
        etree.SubElement(Administration, "To").text = "NBB"
        etree.SubElement(Administration, "Domain").text = "SXX"

    def _node_Item(self, parent, line, decl_code):
        for fld in ("src_dest_country_id", "transaction_id", "region_id", "hs_code_id"):
            if not line[fld]:
                raise UserError(
                    _("Error while processing %s:\nMissing '%s'.")
                    % (line, line._fields[fld].string)
                )
        Item = etree.SubElement(parent, "Item")
        etree.SubElement(Item, "Dim", attrib={"prop": "EXTRF"}).text = decl_code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXCNT"}
        ).text = line.src_dest_country_code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXTTA"}
        ).text = line.transaction_id.code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXREG"}
        ).text = line.region_id.code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXTGO"}
        ).text = line.hs_code_id.local_code
        etree.SubElement(Item, "Dim", attrib={"prop": "EXWEIGHT"}).text = str(
            line.weight
        )
        etree.SubElement(Item, "Dim", attrib={"prop": "EXUNITS"}).text = str(
            line.suppl_unit_qty
        )
        etree.SubElement(Item, "Dim", attrib={"prop": "EXTXVAL"}).text = str(
            line.amount_company_currency
        )
        if self.declaration_type == "dispatches":
            etree.SubElement(
                Item, "Dim", attrib={"prop": "EXCNTORI"}
            ).text = line.product_origin_country_code
            etree.SubElement(Item, "Dim", attrib={"prop": "PARTNERID"}).text = (
                line.vat or ""
            )
        if self.reporting_level == "extended":
            etree.SubElement(
                Item, "Dim", attrib={"prop": "EXTPC"}
            ).text = line.transport_id.code
            etree.SubElement(
                Item, "Dim", attrib={"prop": "EXDELTRM"}
            ).text = line.incoterm_id.code

    def _node_Data(self, parent, decl_code):
        Data = etree.SubElement(parent, "Data")
        Data.set("close", "true")
        if self.declaration_type == "arrivals":
            report_form = "EXF19%s"
        else:
            report_form = "INTRASTAT_X_%sF"
        if self.reporting_level == "standard":
            report_form = report_form % "S"
        else:
            report_form = report_form % "E"
        Data.set("form", report_form)
        if self.action != "nihil":
            for line in self.declaration_line_ids:
                self._node_Item(Data, line, decl_code)

    def _node_Report(self, parent, decl_code):
        Report = etree.SubElement(parent, "Report")
        Report.set("action", self.action)
        Report.set("date", self.year_month)
        if self.declaration_type == "arrivals":
            report_code = "EX19"
        else:
            report_code = "INTRASTAT_X_"
        if self.reporting_level == "standard":
            report_code += "S"
        else:
            report_code += "E"
        Report.set("code", report_code)
        self._node_Data(Report, decl_code)

    def _generate_xml(self):
        self.ensure_one()

        if self.declaration_type == "arrivals":
            decl_code = "19"
            if self.reporting_level == "standard":
                xsd = "ex19s"
            else:
                xsd = "ex19e"
        else:
            decl_code = "29"
            if self.reporting_level == "standard":
                xsd = "intrastat_x_s"
            else:
                xsd = "intrastat_x_e"

        ns_map = {
            None: _INTRASTAT_XMLNS,
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        root = etree.Element("DeclarationReport", nsmap=ns_map)
        self._node_Administration(root)
        self._node_Report(root, decl_code)

        xml_string = etree.tostring(
            root, pretty_print=True, encoding="UTF-8", xml_declaration=True
        )
        module = __name__.split("addons.")[1].split(".")[0]
        self.company_id._intrastat_check_xml_schema(
            xml_string, "{}/static/data/{}.xsd".format(module, xsd)
        )
        return xml_string

    def _xls_computation_line_fields(self):
        res = super()._xls_computation_line_fields()
        i = res.index("product_origin_country")
        res.pop(i)
        return res

    def _xls_declaration_line_fields(self):
        res = super()._xls_declaration_line_fields()
        if self.declaration_type == "dispatches":
            i = res.index("hs_code")
            res.insert(i + 1, "product_origin_country")
        return res


class L10nBeIntrastatProductComputationLine(models.Model):
    _name = "l10n.be.intrastat.product.computation.line"
    _inherit = "intrastat.product.computation.line"
    _description = "Intrastat Product Computation Lines for Belgium"

    parent_id = fields.Many2one(
        comodel_name="l10n.be.intrastat.product.declaration",
        string="Intrastat Product Declaration",
        ondelete="cascade",
        readonly=True,
    )
    declaration_line_id = fields.Many2one(
        comodel_name="l10n.be.intrastat.product.declaration.line",
        string="Declaration Line",
        readonly=True,
    )

    @api.constrains("vat")
    def _check_vat(self):
        for rec in self:
            if not rec.vat == "QV999999999999":
                super(L10nBeIntrastatProductComputationLine, rec)._check_vat()


class L10nBeIntrastatProductDeclarationLine(models.Model):
    _name = "l10n.be.intrastat.product.declaration.line"
    _inherit = "intrastat.product.declaration.line"
    _description = "Intrastat Product Declaration Lines for Belgium"

    parent_id = fields.Many2one(
        comodel_name="l10n.be.intrastat.product.declaration",
        string="Intrastat Product Declaration",
        ondelete="cascade",
        readonly=True,
    )
    computation_line_ids = fields.One2many(
        comodel_name="l10n.be.intrastat.product.computation.line",
        inverse_name="declaration_line_id",
        string="Computation Lines",
        readonly=True,
    )

    @api.constrains("vat")
    def _check_vat(self):
        for rec in self:
            if not rec.vat == "QV999999999999":
                super(L10nBeIntrastatProductDeclarationLine, rec)._check_vat()
