# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs
import time

from odoo import fields, models, api, _
from odoo.exceptions import Warning as UserError


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
        self.ensure_one()
        date_start = self.year + "-01-01"
        date_stop = self.year + "-12-31"

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

