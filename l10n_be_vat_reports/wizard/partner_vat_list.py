# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SC

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

TURNOVER_TAGS = ("00", "01", "02", "03", "45", "49")
VAT_TAGS = ("54", "64")


class PartnerVATList(models.TransientModel):
    _name = "partner.vat.list"
    _description = "Partner VAT list"
    _inherit = ["vat.declaration.mixin"]

    year = fields.Char(
        required=True,
        default=lambda _: str(date.today().year - 1),
    )
    limit_amount = fields.Integer(required=True, default=250)
    partner_ids = fields.Many2many(
        comodel_name="partner.vat.list.client",
        string="Clients",
        help="You can remove clients/partners which you do "
        "not want to show in xml file",
    )
    total_turnover = fields.Float(compute="_compute_totals")
    total_vat = fields.Float("Total VAT", compute="_compute_totals")

    @api.depends("partner_ids")
    def _compute_totals(self):
        for vat_list in self:
            vat_list.total_turnover = round(
                sum(p.turnover for p in vat_list.partner_ids), 2
            )
            vat_list.total_vat = round(
                sum(p.vat_amount for p in vat_list.partner_ids), 2
            )

    def get_partners(self):
        self.ensure_one()
        date_from = date(int(self.year), 1, 1)
        date_to = date(int(self.year), 12, 31)

        partner_vat_list_client_model = self.env["partner.vat.list.client"]
        partners = partner_vat_list_client_model.browse([])
        be_id = self.env.ref("base.be").id
        turnover_tags_ids = []
        vat_tags_ids = []
        for tag in TURNOVER_TAGS:
            turnover_tags_ids += (
                self.env["account.account.tag"]._get_tax_tags(tag, be_id).mapped("id")
            )
        for tag in VAT_TAGS:
            vat_tags_ids += (
                self.env["account.account.tag"]._get_tax_tags(tag, be_id).mapped("id")
            )

        # query explanation:
        #
        # first, select all account tags corresponding to the tag names
        # (turnover_tags and vat_tags). the name column of account_account_tag
        # cannot be used directly because each tag exists twice (with a + and
        # - prefix), the tag_name column of account_tax_report_line must be
        # used instead.
        #
        # then, for each partner, perform 2 subqueries doing basically the
        # same thing, which is summing the balance of all account move lines
        # (of posted account moves, to ignore draft and cancelled ones)
        # corresponding to these tags.
        #
        # for turnover tags, the account move lines are directly linked to the
        # tags (through account_account_tag_account_move_line_rel). for vat
        # tags, it is a little more complicated because the tags are linked to
        # the account tax linked to the account move line (through
        # account_tax_repartition_line and
        # account_account_tag_account_tax_repartition_line_rel).
        #
        # for each of these subqueries, an exists condition with a subquery is
        # used (instead of joining directly) because multiple tags can be
        # linked to the same account move line. joining directly would result
        # in account move lines being present as many times as the number of
        # tags linked to them, which would multiply their balance accordingly
        # in the sum.
        #
        # finally, a condition limits the result to partners having a belgian
        # vat number and for which the turnover sum is at least limit_amount.
        query = """
select
    rp.name,
    rp.vat,
    aml1.total_amount as turnover,
    coalesce(aml2.total_amount, 0.00) as vat_amount
from
    res_partner as rp
inner join (
    select
        aml.partner_id,
        round(sum(-aml.balance), 2) as total_amount
    from account_move_line as aml
    inner join account_move as am on
        aml.move_id = am.id and
        am.state = 'posted'
    where aml.date between %(date_from)s and %(date_to)s and
        aml.company_id = %(company_id)s
    and exists (
        select 1
        from account_account_tag_account_move_line_rel as aatamlr
        where aatamlr.account_move_line_id = aml.id
        and aatamlr.account_account_tag_id in %(turnover_tags_ids)s)
    group by 1) as aml1 on
    aml1.partner_id = rp.id
left join (
    select
        aml.partner_id,
        round(sum(-aml.balance), 2) as total_amount
    from account_move_line as aml
    inner join account_move as am on
        aml.move_id = am.id and
        am.state = 'posted'
    where aml.date between %(date_from)s and %(date_to)s and
        aml.company_id = %(company_id)s
    and exists (
        select 1
        from account_tax as at
        inner join account_tax_repartition_line as atrl on
            at.id in (atrl.invoice_tax_id, atrl.refund_tax_id)
        inner join account_account_tag_account_tax_repartition_line_rel
            as aatatrlr on
            aatatrlr.account_tax_repartition_line_id = atrl.id
        where at.id = aml.tax_line_id
        and aatatrlr.account_account_tag_id in %(vat_tags_ids)s)
    group by 1) as aml2 on
    aml2.partner_id = rp.id
where
    rp.vat ilike 'be%%' and
    aml1.total_amount >= %(limit_amount)s
        """
        args = {
            "turnover_tags_ids": tuple(turnover_tags_ids),
            "vat_tags_ids": tuple(vat_tags_ids),
            "date_from": date_from,
            "date_to": date_to,
            "company_id": self.env.company.id,
            "limit_amount": self.limit_amount,
        }
        self.env.cr.execute(query, args)
        for seq, record in enumerate(self.env.cr.dictfetchall(), start=1):
            record["vat"] = self.env["res.partner"].fix_eu_vat_number(
                be_id, record["vat"]
            )
            record["seq"] = seq
            partners |= partner_vat_list_client_model.create(record)

        if not partners:
            raise UserError(_("No data found for the selected year."))

        resource_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "l10n_be_vat_reports.partner_vat_list_view_form_clients"
        )
        self.partner_ids = partners.ids
        return {
            "name": _("VAT Listing"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.list",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "inline",
        }

    def create_xml(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_be_vat_reports.l10n_be_vat_listing_consignment_xml_report"
        ).report_action(self, config=False)

    def print_vatlist(self):
        self.ensure_one()

        if not self.partner_ids:
            raise UserError(_("No record to print."))

        return self.env.ref(
            "l10n_be_vat_reports.action_report_l10nvatpartnerlisting"
        ).report_action(self)
