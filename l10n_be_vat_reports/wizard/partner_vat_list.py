# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning as UserError


class PartnerVATList(models.TransientModel):
    """ Partner Vat Listing """
    # todo better model naming
    _name = "partner.vat.list"
    _description = "Partner VAT list"

    partner_ids = fields.Many2many(
        comodel_name="vat.listing.clients",
        relation="vat_partner_rel",
        column1="vat_id",
        column2="partner_id",
        string="Clients",
        help="You can remove clients/partners which you do "
        "not want to show in xml file",
    )
    declarant_reference = fields.Char(
        compute="_compute_declarant_reference"
    )
    name = fields.Char("File Name")
    year = fields.Char("Year")
    limit_amount = fields.Float("Limit Amount")
    file_save = fields.Binary("Save File", readonly=True)
    comments = fields.Text("Comments")
    total_turnover = fields.Float("Total Turnover", compute="_compute_totals")
    total_vat = fields.Float("Total VAT", compute="_compute_totals")

    @api.multi
    def _compute_declarant_reference(self):

        self.env["ir.sequence"].next_by_code("declarantnum")
        company = self.env.user.company_id
        company_vat = company.partner_id.vat

        if not company_vat:
            raise ValidationError(_("No VAT number associated with the company."))

        company_vat = company_vat.replace(" ", "").upper()
        for listing in self:
            seq_declarantnum = self.env["ir.sequence"].next_by_code("declarantnum")
            listing.declarant_reference = company_vat[2:] + seq_declarantnum[-4:]

    @api.multi
    def _compute_totals(self):
        for vat_list in self:
            vat_list.total_turnover = sum(
                p.turnover for p in vat_list.partner_ids
            )
            vat_list.total_vat = sum(
                p.vat_amount for p in vat_list.partner_ids
            )

    @api.multi
    def _get_datas(self):
        self.ensure_one()
        datas = self.partner_ids.read()
        client_datas = []
        seq = 0
        sum_tax = 0.00
        sum_turnover = 0.00
        amount_data = {}
        for line in datas:
            if not line:
                continue
            seq += 1
            sum_tax += line["vat_amount"]
            sum_turnover += line["turnover"]
            vat = line["vat"]
            vat = self._format_vat_number(vat)
            amount_data = {
                "seq": str(seq),
                "vat": vat,
                "only_vat": vat,
                "turnover": "%.2f" % line["turnover"],
                "vat_amount": "%.2f" % line["vat_amount"],
                "sum_tax": "%.2f" % sum_tax,
                "sum_turnover": "%.2f" % sum_turnover,
                "partner_name": line["name"],
            }
            client_datas += [amount_data]
        return client_datas

    @api.multi
    def create_xml(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_be_vat_reports.l10n_be_vat_listing_consignment_xml_report"
        ).report_action(self, config=False)

    @api.multi
    def print_vatlist(self):
        self.ensure_one()

        if not self.partner_ids:
            raise UserError(_("No record to print."))

        return self.env.ref(
            "l10n_be_vat_reports.action_report_l10nvatpartnerlisting"
        ).report_action(self)
