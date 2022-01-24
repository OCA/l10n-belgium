# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs
import time
import base64
import re

from odoo import fields, models, api, _
from odoo.exceptions import Warning as UserError
from odoo.exceptions import ValidationError


class VATListingClients(models.TransientModel):
    # todo better model naming
    _name = "vat.listing.clients"
    _description = "VAT Listing Clients"

    seq = fields.Integer("Sequence")
    name = fields.Char("Client Name", help="Used as file name.")
    vat = fields.Char("VAT")
    turnover = fields.Float("Base Amount")
    vat_amount = fields.Float("VAT Amount")

    @api.multi
    @api.constrains("vat")
    def _check_vat_number(self):
        """
        Belgium VAT numbers must respect this pattern: 0[1-9]{1}[0-9]{8}
        """
        be_vat_pattern = re.compile(r"BE0[1-9]{1}[0-9]{8}")
        for client in self:
            if not be_vat_pattern.match(client.vat):
                raise ValidationError(
                    _(
                        "Belgian Intervat platform only accepts VAT numbers "
                        "matching this pattern: 0[1-9]{1}[0-9]{8} (number "
                        "part). Check vat number %s for client %s"
                    )
                    % (client.vat, client.name)
                )


class PartnerVAT(models.TransientModel):
    # todo better model naming
    _name = "partner.vat"
    _description = "Partner VAT"

    year = fields.Char(
        "Year",
        size=4,
        required=True,
        default=lambda *a: str(int(time.strftime("%Y")) - 1),
    )
    limit_amount = fields.Integer("Limit Amount", required=True, default=250)

    @api.multi
    def get_partners(self):
        year = self.year
        date_start = year + "-01-01"
        date_stop = year + "-12-31"

        partners = self.env["vat.listing.clients"].browse([])
        be_partners = self.env["res.partner"].search([("vat", "ilike", "BE%")])
        if not be_partners:
            raise UserError(
                _("No belgium contact with a VAT number in your database.")
            )
        query = """
WITH turnover_tags AS
  (SELECT tagsrel.account_tax_id
   FROM account_tax_account_tag tagsrel
   INNER JOIN ir_model_data tag_xmlid ON (
       tag_xmlid.model = 'account.account.tag'
       AND tagsrel.account_account_tag_id = tag_xmlid.res_id)
   WHERE tag_xmlid.NAME IN ('tax_tag_00',
                            'tax_tag_01',
                            'tax_tag_02',
                            'tax_tag_03',
                            'tax_tag_45',
                            'tax_tag_49'))
, vat_amount_tags AS
  (SELECT tagsrel.account_tax_id
   FROM account_tax_account_tag tagsrel
   INNER JOIN ir_model_data tag_xmlid ON (
       tag_xmlid.model = 'account.account.tag'
       AND tagsrel.account_account_tag_id = tag_xmlid.res_id)
   WHERE tag_xmlid.NAME IN ('tax_tag_54',
                            'tax_tag_64'))
SELECT sub1.NAME,
       sub1.vat,
       COALESCE(sub1.turnover, 0) AS turnover,
       COALESCE(sub2.vat_amount, 0) AS vat_amount
FROM
  (SELECT l.partner_id,
          p.NAME,
          p.vat,
          Sum(-l.balance) AS turnover
   FROM account_move_line l
   LEFT JOIN res_partner p ON l.partner_id = p.id
   WHERE l.partner_id IN %s
         AND l.date BETWEEN %s AND %s
         AND EXISTS
           (SELECT 1
            FROM account_move_line_account_tax_rel taxrel
            WHERE taxrel.account_move_line_id = l.id
              AND taxrel.account_tax_id IN
                (SELECT account_tax_id
                 FROM turnover_tags) )
   GROUP BY l.partner_id,
            p.NAME,
            p.vat) AS sub1
LEFT JOIN
  (SELECT l2.partner_id,
          Sum(-l2.balance) AS vat_amount
   FROM account_move_line l2
   WHERE l2.partner_id IN %s
         AND l2.date BETWEEN %s AND %s
         AND EXISTS
           (SELECT 1
            FROM vat_amount_tags
            WHERE account_tax_id = l2.tax_line_id)
   GROUP BY partner_id) AS sub2 ON sub1.partner_id = sub2.partner_id;
        """
        args = (
            tuple(be_partners.ids),
            date_start,
            date_stop,
            tuple(be_partners.ids),
            date_start,
            date_stop,
        )
        self.env.cr.execute(query, args)
        seq = 0
        for record in self.env.cr.dictfetchall():
            record["vat"] = record["vat"].replace(" ", "").upper()
            if record["turnover"] >= self.limit_amount:
                seq += 1
                record["seq"] = seq
                partners |= self.env["vat.listing.clients"].create(record)

        if not partners:
            raise UserError(_("No data found for the selected year."))

        model_datas = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("name", "=", "view_vat_listing")],
            limit=1,
        )
        resource_id = model_datas.res_id
        partner_vat_list = self.env["partner.vat.list"].create(
            {
                "name": _("%s Annual Listing Preview.xml") % self.year,
                "year": self.year,
                "limit_amount": self.limit_amount,
                "partner_ids": [(6, 0, partners.ids)],
            }
        )
        return {
            "name": _("Vat Listing"),
            "res_id": partner_vat_list.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.list",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "inline",
        }


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
        # todo use OCA module report_xml
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
