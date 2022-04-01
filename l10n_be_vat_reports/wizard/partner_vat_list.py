# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning as UserError
from datetime import date


class PartnerVATList(models.TransientModel):
    _name = "partner.vat.list"
    _description = "Partner VAT list"

    year = fields.Char(
        "Year",
        size=4,
        required=True,
        default=lambda _: str(date.today().year - 1),
    )
    limit_amount = fields.Integer("Limit Amount", required=True, default=250)
    partner_ids = fields.Many2many(
        comodel_name="partner.vat.list.client",
        string="Clients",
        help="You can remove clients/partners which you do "
        "not want to show in xml file",
    )
    declarant_reference = fields.Char(compute="_compute_declarant_reference")
    total_turnover = fields.Float("Total Turnover", compute="_compute_totals")
    total_vat = fields.Float("Total VAT", compute="_compute_totals")
    comments = fields.Text("Comments")

    @api.multi
    def _compute_declarant_reference(self):
        self.env["ir.sequence"].next_by_code("declarantnum")
        company = self.env.user.company_id
        company_vat = company.partner_id.vat

        if not company_vat:
            raise ValidationError(
                _("No VAT number associated with your company.")
            )

        company_vat = company_vat.replace(" ", "").upper()
        for listing in self:
            seq_declarantnum = self.env["ir.sequence"].next_by_code(
                "declarantnum"
            )
            listing.declarant_reference = (
                company_vat[2:] + seq_declarantnum[-4:]
            )

    @api.multi
    @api.depends("partner_ids")
    def _compute_totals(self):
        for vat_list in self:
            vat_list.total_turnover = round(sum(
                p.turnover for p in vat_list.partner_ids
            ), 2)
            vat_list.total_vat = round(sum(
                p.vat_amount for p in vat_list.partner_ids
            ), 2)

    @api.multi
    def get_partners(self):
        self.ensure_one()
        date_start = date(int(self.year), 1, 1)
        date_stop = date(int(self.year), 12, 31)

        partners = self.env["partner.vat.list.client"].browse([])
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
           ROUND(COALESCE(sub1.turnover, 0), 2) AS turnover,
           ROUND(COALESCE(sub2.vat_amount, 0), 2) AS vat_amount
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
            date_start.isoformat(),
            date_stop.isoformat(),
            tuple(be_partners.ids),
            date_start.isoformat(),
            date_stop.isoformat(),
        )
        self.env.cr.execute(query, args)
        seq = 0
        for record in self.env.cr.dictfetchall():
            record["vat"] = record["vat"].replace(" ", "").upper()
            if record["turnover"] >= self.limit_amount:
                seq += 1
                record["seq"] = seq
                partners |= self.env["partner.vat.list.client"].create(record)

        if not partners:
            raise UserError(_("No data found for the selected year."))

        model_datas = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.ui.view"),
                ("name", "=", "partner_vat_list_view_form_clients")
            ],
            limit=1,
        )
        resource_id = model_datas.res_id
        self.partner_ids = partners.ids
        return {
            "name": _("Vat Listing"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.list",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "inline",
        }

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
