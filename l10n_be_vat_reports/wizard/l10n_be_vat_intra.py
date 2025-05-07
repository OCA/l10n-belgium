# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SC
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError

TAX_TAGS_DICT = {
    "44": "S",
    "46L": "L",
    "46T": "T",
    "48s44": "S",
    "48s46L": "L",
    "48s46T": "T",
}


class PartnerVATIntra(models.TransientModel):
    """
    Partner Vat Intra Wizard
    """

    _name = "partner.vat.intra"
    _description = "Partner VAT Intra"
    _inherit = ["vat.declaration.mixin"]

    @api.model
    def _get_europe_country(self):
        return self.env["res.country"].search(
            [
                (
                    "code",
                    "in",
                    [
                        "AT",
                        "BG",
                        "CY",
                        "CZ",
                        "DK",
                        "EE",
                        "FI",
                        "FR",
                        "DE",
                        "GR",
                        "HU",
                        "IE",
                        "IT",
                        "LV",
                        "LT",
                        "LU",
                        "MT",
                        "NL",
                        "PL",
                        "PT",
                        "RO",
                        "SK",
                        "SI",
                        "ES",
                        "SE",
                        "GB",
                    ],
                )
            ]
        )

    period_code = fields.Char(
        required=True,
        help="""This is where you have to set the period code for the """
        """intracom declaration using the format: ppyyyy
               PP can stand for a month: from '01' to '12'.
               PP can stand for a trimester: '31','32','33','34'
                   The first figure means that it is a trimester
                   The second figure identify the trimester.
               PP can stand for a complete fiscal year: '00'.
               YYYY stands for the year (4 positions).""",
    )
    month = fields.Integer(compute="_compute_period")
    quarter = fields.Integer(compute="_compute_period")
    year = fields.Integer(compute="_compute_period")
    date_start = fields.Date("Start date", required=True)
    date_end = fields.Date("End date", required=True)
    test_xml = fields.Boolean("Test XML file", help="Sets the XML output as test file")
    country_ids = fields.Many2many(
        "res.country",
        "vat_country_rel",
        "vat_id",
        "country_id",
        "European Countries",
        default=_get_europe_country,
    )
    client_ids = fields.Many2many(
        comodel_name="vat.intra.client",
        relation="vat_intra_client_rel",
        column1="vat_intra_id",
        column2="client_id",
        string="Clients",
        help="You can remove clients/partners which you do "
        "not want to show in xml file",
    )
    partner_wo_vat = fields.Integer(
        string="Partner without VAT", compute="_compute_sums"
    )
    amount_total = fields.Float(compute="_compute_sums")

    @api.depends("period_code")
    def _compute_period(self):
        for vat_intra in self:
            month_quarter = vat_intra.period_code[:2]
            if month_quarter.startswith("3"):
                vat_intra.month = False
                vat_intra.quarter = int(month_quarter[1])
            elif month_quarter.startswith("0") and month_quarter.endswith("0"):
                vat_intra.month = False
                vat_intra.quarter = False
            else:
                vat_intra.month = int(month_quarter)
                vat_intra.quarter = False
            vat_intra.year = vat_intra.period_code[2:]

    @api.depends("client_ids")
    def _compute_sums(self):
        for vat_intra in self:
            clients = vat_intra.client_ids
            vat_intra.partner_wo_vat = len([c for c in clients if not c.vat])
            vat_intra.amount_total = sum(c.amount for c in clients)

    @api.constrains("period_code")
    def _check_period_code(self):
        for rec in self:
            if len(rec.period_code) != 6:
                raise UserError(_("Period code is not valid."))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if not rec.date_start <= rec.date_end:
                raise UserError(_("Start date cannot be after the end date."))

    def get_partners(self):
        self.ensure_one()
        be_id = self.env.ref("base.be").id
        tax_tags_ids = []
        for tag in TAX_TAGS_DICT.keys():
            tax_tags_ids += (
                self.env["account.account.tag"]._get_tax_tags(tag, be_id).mapped("id")
            )

        # query explanation:
        #
        # first, select all account tags corresponding to the tag names (keys
        # of tax_tags). the name column of account_account_tag cannot be
        # used directly because each tag exists twice (with a + and - prefix),
        # the tag_name column of account_tax_report_line must be used instead.
        # note that each tag name must appear only once in
        # account_tax_report_line, otherwise the totals will be incorrect.
        # this is the case if only the standard l10n_be module is installed.
        #
        # then, sum the balance of all account move lines (of posted account
        # moves, to ignore draft and cancelled ones) corresponding to these
        # tags, grouping by partner and tag.
        query = """
select
    rp.name as partner_name,
    rp.vat,
    aatamlr.account_account_tag_id as intra_code_id,
    round(sum(-aml.balance), 2) as amount
from account_move_line as aml
inner join account_move as am on
    aml.move_id = am.id and
    am.state = 'posted'
inner join account_account_tag_account_move_line_rel as aatamlr on
    aatamlr.account_move_line_id = aml.id
left join res_partner as rp on
    aml.partner_id = rp.id
where
    aml.date between %s and %s and
    aml.company_id = %s and
    aatamlr.account_account_tag_id in %s
group by 1, 2, 3
        """
        company_id = self.env.company.id
        self.env.cr.execute(
            query, (self.date_start, self.date_end, company_id, tuple(tax_tags_ids))
        )

        vat_intra_client_model = self.env["vat.intra.client"]
        clients = vat_intra_client_model.browse()
        for seq, row in enumerate(self.env.cr.dictfetchall(), start=1):
            amount = row["amount"] or 0.0
            tax_tag = self.env["account.account.tag"].browse(row["intra_code_id"]).name
            tax_tag_no_sign = tax_tag.replace("+", "").replace("-", "")
            code = TAX_TAGS_DICT.get(tax_tag_no_sign, "")
            vat = row.get("vat") or ""
            vat = vat.replace(" ", "").upper()

            client_data = {
                "seq": seq,
                "partner_name": row["partner_name"],
                "vat": vat,
                "vatnum": vat[2:],
                "country": vat[:2],
                "intra_code": tax_tag,
                "code": code,
                "amount": amount,
            }
            client = vat_intra_client_model.create(client_data)
            clients |= client

        self.client_ids = clients

        resource_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "l10n_be_vat_reports.view_vat_intra"
        )
        return {
            "name": _("VAT Intra Listing"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.intra",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "inline",
        }

    def get_company_address(self, company):
        address = company.partner_id.address_get(["invoice"])

        if address.get("invoice"):
            ads = self.env["res.partner"].browse([address["invoice"]])
            city = ads.city or ""
            post_code = ads.zip or ""
            country = ads.country_id.code if ads.country_id else ""

            if ads.street and ads.street2:
                street = "%s %s" % (ads.street, ads.street2)
            elif ads.street:
                street = ads.street
            else:
                street = ""

            address_data = {
                "street": street,
                "city": city,
                "post_code": post_code,
                "country": country,
            }

        else:
            address_data = {
                "street": "",
                "city": "",
                "post_code": "",
                "country": "",
            }

        return address_data

    def _get_data(self):
        self.ensure_one()

        # company data
        company = self.env.company
        company_vat = company.partner_id.vat
        if not company_vat:
            raise UserError(_("No VAT number associated with your company."))
        company_vat = company_vat.replace(" ", "").upper()
        email = company.partner_id.email or ""
        phone = company.partner_id.phone or ""
        company_address = self.get_company_address(company)

        # report data
        seq_declarantnum = self.env["ir.sequence"].next_by_code("declarantnum")
        dnum = company_vat[2:] + seq_declarantnum[-4:]

        client_list = self.client_ids.to_dict()

        data = {
            "company_name": company.name,
            "company_vat": company_vat,
            "vatnum": company_vat[2:],
            "mand_id": self.mand_id,
            "sender_date": str(time.strftime("%Y-%m-%d")),
            "email": email,
            "phone": phone,
            "period": self.period_code,
            "clientlist": client_list,
            "comments": self.comments,
            "issued_by": company_vat[:2],
            "dnum": dnum,
            "clientnbr": str(len(self.client_ids)),
            "amountsum": round(self.amount_total, 2),
            "partner_wo_vat": self.partner_wo_vat,
        }
        data.update(company_address)
        return data

    def create_xml(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_be_vat_reports.l10n_be_vat_intra_consignment_xml_report"
        ).report_action(self, config=False)

    def print_vat_intra(self):
        self.ensure_one()

        if not self.client_ids:
            raise UserError(_("No record to print."))

        return self.env.ref(
            "l10n_be_vat_reports.action_report_l10nvatintraprint"
        ).report_action(self)
