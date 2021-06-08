# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import re

from odoo import api, fields, models


class BeVATDeclarationWizard(models.TransientModel):
    _name = "be.vat.declaration.wizard"
    _description = "Wizard to get values needed in xml vat declaration"

    mr_instance_id = fields.Many2one(
        comodel_name="mis.report.instance",
        string="Mis Report Instance",
        required=True,
    )
    client_listing_nihil = fields.Boolean(
        string="Client Listing Nihil",
        help="Only applies to the last civil declaration"
        " or the declaration linked to the cessaction of activity:"
        " no customer to list in the customer listing",
    )
    ask_restitution = fields.Boolean(
        string="Ask restitution",
    )
    ask_payment = fields.Boolean(
        string="Ask payment form",
    )
    grid_91 = fields.Float(
        string="Grid 91",
        required=False,
        help="Only applies to december monthly declaration:"
        " Amount declared for grid 91: VAT due from due "
        " for the period from the 1st to the 20th of december",
    )
    period = fields.Selection(
        string="Period",
        selection=[("month", "Month"), ("quarter", "Quarter")],
        default="month",
        required=True,
        help="Month or Quarter value is compute from the report start date.",
    )
    period_value = fields.Integer(
        string="Period Value",
        compute="_compute_period_value",
    )
    declarant_vat = fields.Char(
        string="Declarant Tax ID",
        compute="_compute_declarant_vat",
    )
    declarant_phone = fields.Char(
        string="Declarant Phone",
        compute="_compute_declarant_phone",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        mr_instance = self.env.context["active_id"]
        defaults["mr_instance_id"] = mr_instance
        return defaults

    def generate_xml(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_be_mis_reports_xml.l10n_be_vat_declaration_xml_report"
        ).report_action(self)

    def prepare_xml_data(self):
        self.ensure_one()
        kpi_matrix_dict = self.mr_instance_id.compute()
        data = {
            row["row_id"]: row["cells"][0]["val"]
            for row in kpi_matrix_dict["body"]
        }

        data = {
            k: "{:.2f}".format(round(v, 2))
            for k, v in data.items()
            if k.startswith("grid") and v
        }
        return data

    def compute_declarant_reference(self):
        return self.env["ir.sequence"].next_by_code(
            "be.vat.declaration.declarant"
        )

    @api.multi
    @api.depends("mr_instance_id.date_from", "period")
    def _compute_period_value(self):
        self.ensure_one()
        date_from = self.mr_instance_id.date_from
        if self.period == "month":
            self.period_value = date_from.month
        else:
            self.period_value = (date_from.month - 1) // 3 + 1

    @api.multi
    @api.depends("mr_instance_id.company_id")
    def _compute_declarant_vat(self):
        for rec in self:
            company = rec.mr_instance_id.company_id
            rec.declarant_vat = re.sub(r"\D", "", company.vat)

    @api.multi
    @api.depends("mr_instance_id.company_id")
    def _compute_declarant_phone(self):
        for rec in self:
            company = rec.mr_instance_id.company_id
            rec.declarant_phone = re.sub(
                r"\D", "", re.sub(r"\+", r"00", company.phone)
            )
