# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)

_render = ReportXlsxAbstract._render
_logger = logging.getLogger(__name__)

_INTRASTAT_XMLNS = "http://www.onegate.eu/2010-01-01"


class IntrastatProductDeclaration(models.Model):
    _inherit = "intrastat.product.declaration"

    def _get_region(self, inv_line, notedict):
        region = super()._get_region(inv_line, notedict)
        if self.company_country_code == "BE" and not region:
            msg = _(
                "The Intrastat Region of the Company is not set, "
                "please configure it first."
            )
            self._account_config_warning(msg)
        return region

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
        if self.company_country_code != "BE":
            return
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
                                "hs_code_id": notedict["credit_note_code_origin"].id,
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
                                "hs_code_id": notedict["credit_note_code_origin"].id,
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
            msg = _(
                "Unable to determine the correct handling of Refund. "
                "Please check/set the Intrastat Transaction Code on the Refund."
            )
            notedict["invoice"][notedict["inv_origin"]].add(msg)

    def _update_computation_line_vals(self, inv_line, line_vals, notedict):
        super()._update_computation_line_vals(inv_line, line_vals, notedict)
        # handling of refunds
        if self.company_country_code == "BE":
            inv = inv_line.move_id
            if inv.move_type in ["in_refund", "out_refund"]:
                self._handle_refund(inv_line, line_vals, notedict)

            if line_vals:
                # extended declaration
                if self.reporting_level == "extended":
                    incoterm = self._get_incoterm(inv_line, notedict)
                    line_vals.update({"incoterm_id": incoterm.id})
        return

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
        if self.company_country_code != "BE":
            return super()._handle_invoice_accessory_cost(
                invoice,
                lines_current_invoice,
                total_inv_accessory_costs_cc,
                total_inv_product_cc,
                total_inv_weight,
            )
        else:
            return

    def _gather_invoices_init(self, notedict):
        if self.company_country_code == "BE":
            # Special commodity codes
            # Current version implements only regular credit notes
            special_code = "99600000"
            hs_code = self.env["hs.code"].search(
                [
                    ("local_code", "=", special_code),
                    "|",
                    ("company_id", "=", self.company_id.id),
                    ("company_id", "=", False),
                ],
                limit=1,
            )
            if not hs_code:
                msg = (
                    _(
                        "Intrastat Code '%s' not found. "
                        "\nYou can update your codes "
                        "via the module intrastat_product_hscodes_import."
                    )
                    % special_code
                )
                raise UserError(msg)
            notedict.update(
                {
                    "credit_note_code_origin": hs_code,
                }
            )
        else:
            return super()._gather_invoices_init(notedict)

    def _sanitize_vat(self, vat):
        return vat and vat.replace(" ", "").replace(".", "").upper()

    def _check_generate_xml(self):
        self.ensure_one()
        res = super()._check_generate_xml()
        if self.company_country_code == "BE":
            if not self.declaration_line_ids:
                res = self.generate_declaration()
        return res

    def _get_kbo_bce_nr(self):
        kbo_bce_nr = False
        vat = self._sanitize_vat(self.company_id.vat)
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
        for fld in (
            "src_dest_country_code",
            "transaction_id",
            "region_code",
            "hs_code_id",
        ):
            if not line[fld]:
                raise UserError(
                    _("Error while processing %(line)s:\nMissing '%(line_field)s'.")
                    % {"line": line, "line_field": line._fields[fld].string}
                )
        Item = etree.SubElement(parent, "Item")
        etree.SubElement(Item, "Dim", attrib={"prop": "EXTRF"}).text = decl_code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXCNT"}
        ).text = line.src_dest_country_code
        etree.SubElement(
            Item, "Dim", attrib={"prop": "EXTTA"}
        ).text = line.transaction_id.code
        etree.SubElement(Item, "Dim", attrib={"prop": "EXREG"}).text = line.region_code
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
        if self.company_country_code == "BE":
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
                xml_string, f"{module}/static/data/{xsd}.xsd"
            )
            return xml_string
        else:
            return super()._generate_xml()

    def _xls_computation_line_fields(self):
        res = super()._xls_computation_line_fields()
        if self.company_country_code == "BE":
            i = res.index("product_origin_country")
            res.pop(i)
        return res

    def _xls_declaration_line_fields(self):
        res = super()._xls_declaration_line_fields()
        if self.company_country_code == "BE":
            if self.declaration_type == "dispatches":
                i = res.index("hs_code")
                res.insert(i + 1, "product_origin_country")
        return res


class IntrastatProductComputationLine(models.Model):
    _inherit = "intrastat.product.computation.line"
    _description = "Intrastat Product Computation Lines for Belgium"

    @api.depends("partner_id")
    def _compute_vat(self):
        for rec in self:
            if rec.company_country_code == "BE" and (
                rec.invoice_id.fiscal_position_id.intrastat == "b2c"
                or (
                    rec.invoice_id.fiscal_position_id.intrastat == "b2b"
                    and (
                        not rec.invoice_id.fiscal_position_id.vat_required
                        or (
                            rec.partner_id.vat
                            and rec.partner_id.vat.lower().strip() == "na"
                        )
                    )
                )
            ):
                rec.vat = "QV999999999999"
            else:
                super(IntrastatProductComputationLine, rec)._compute_vat()
        return

    @api.constrains("vat")
    def _check_vat(self):
        for rec in self:
            if not rec.vat == "QV999999999999":
                super(IntrastatProductComputationLine, rec)._check_vat()
        return

    def _group_line_hashcode_fields(self):
        res = super()._group_line_hashcode_fields()
        if self.company_country_code == "BE":
            if self.declaration_type == "arrivals":
                del res["product_origin_country"]
                del res["vat"]
            if self.reporting_level == "extended":
                res["incoterm"] = self.incoterm_id.id or False
        return res

    def _prepare_grouped_fields(self, fields_to_sum):
        vals = super()._prepare_grouped_fields(fields_to_sum)
        if self.reporting_level == "extended":
            vals["incoterm_id"] = self.incoterm_id.id
        return vals
