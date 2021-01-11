# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs
import time
import base64

from odoo import fields, models, api, _
from odoo.exceptions import Warning as UserError


class VATListingClients(models.TransientModel):
    _name = "vat.listing.clients"
    _description = "VAT Listing Clients"

    seq = fields.Integer("Sequence")
    name = fields.Char("Client Name")
    vat = fields.Char("VAT")
    turnover = fields.Float("Base Amount")
    vat_amount = fields.Float("VAT Amount")


class PartnerVAT(models.TransientModel):
    """ Vat Listing """

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
                _("No belgium contact with a VAT number " "in your database.")
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
                "name": _("%s Annual Listing Preview") % self.year,
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
    name = fields.Char("File Name")
    year = fields.Char("Year")
    limit_amount = fields.Float("Limit Amount")
    file_save = fields.Binary("Save File", readonly=True)
    comments = fields.Text("Comments")
    total_turnover = fields.Float("Total Turnover", compute="_compute_totals")
    total_vat = fields.Float("Total VAT", compute="_compute_totals")

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
            vat = line["vat"].replace(" ", "").upper()
            amount_data = {
                "seq": str(seq),
                "vat": vat,
                "only_vat": vat[2:],
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
        self.env["ir.sequence"].next_by_code("declarantnum")
        obj_cmpny = self.env.user.company_id
        company_vat = obj_cmpny.partner_id.vat

        if not company_vat:
            raise UserError(_("No VAT number associated with the company."))

        company_vat = company_vat.replace(" ", "").upper()
        SenderId = company_vat[2:]
        issued_by = company_vat[:2]
        seq_declarantnum = self.env["ir.sequence"].next_by_code("declarantnum")
        dnum = company_vat[2:] + seq_declarantnum[-4:]
        street = city = country = ""
        addr = obj_cmpny.partner_id.address_get(["invoice"])
        if addr.get("invoice", False):
            ads = self.env["res.partner"].browse([addr["invoice"]])
            phone = ads.phone and ads.phone.replace(" ", "") or ""
            email = ads.email or ""
            city = ads.city or ""
            _zip = ads.zip or ""
            if not city:
                city = ""
            if ads.street:
                street = ads.street
            if ads.street2:
                street += " " + ads.street2
            if ads.country_id:
                country = ads.country_id.code

        comp_name = obj_cmpny.name

        if not email:
            raise UserError(_("No email address associated with the company."))
        if not phone:
            raise UserError(_("No phone associated with the company."))
        annual_listing_data = {
            "issued_by": issued_by,
            "company_vat": company_vat,
            "comp_name": comp_name,
            "street": street,
            "zip": _zip,
            "city": city,
            "country": country,
            "email": email,
            "phone": phone,
            "SenderId": SenderId,
            "period": self.year,
            "comments": self.comments if self.comments else "",
        }

        data_file = """<?xml version="1.0" encoding="UTF-8"?>
<ns2:ClientListingConsignment xmlns="http://www.minfin.fgov.be/InputCommon"
 xmlns:ns2="http://www.minfin.fgov.be/ClientListingConsignment"
 ClientListingsNbr="1">
    <ns2:Representative>
        <RepresentativeID identificationType="NVAT"
         issuedBy="%(issued_by)s">%(SenderId)s</RepresentativeID>
        <Name>%(comp_name)s</Name>
        <Street>%(street)s</Street>
        <PostCode>%(zip)s</PostCode>
        <City>%(city)s</City>"""
        if annual_listing_data["country"]:
            data_file += "\n\t\t<CountryCode>%(country)s</CountryCode>"
        data_file += """
        <EmailAddress>%(email)s</EmailAddress>
        <Phone>%(phone)s</Phone>
    </ns2:Representative>"""
        data_file = data_file % annual_listing_data

        data_comp = (
            """
        <ns2:Declarant>
            <VATNumber>%(SenderId)s</VATNumber>
            <Name>%(comp_name)s</Name>
            <Street>%(street)s</Street>
            <PostCode>%(zip)s</PostCode>
            <City>%(city)s</City>
            <CountryCode>%(country)s</CountryCode>
            <EmailAddress>%(email)s</EmailAddress>
            <Phone>%(phone)s</Phone>
        </ns2:Declarant>
        <ns2:Period>%(period)s</ns2:Period>
        """
            % annual_listing_data
        )

        # Turnover and Farmer tags are not included
        client_datas = self._get_datas()
        if not client_datas:
            raise UserError(_("No data available for the client."))
        data_client_info = ""
        for amount_data in client_datas:
            data_client_info += (
                """
    <ns2:Client SequenceNumber="%(seq)s">
        <ns2:CompanyVATNumber issuedBy="BE">%(only_vat)s</ns2:CompanyVATNumber>
        <ns2:TurnOver>%(turnover)s</ns2:TurnOver>
        <ns2:VATAmount>%(vat_amount)s</ns2:VATAmount>
    </ns2:Client>"""
                % amount_data
            )

        amount_data_begin = client_datas[-1]
        amount_data_begin.update({"dnum": dnum})
        data_begin = (
            """
    <ns2:ClientListing SequenceNumber="1" ClientsNbr="%(seq)s"
     DeclarantReference="%(dnum)s"
        TurnOverSum="%(sum_turnover)s" VATAmountSum="%(sum_tax)s">
"""
            % amount_data_begin
        )

        data_end = (
            """

        <ns2:Comment>%(comments)s</ns2:Comment>
    </ns2:ClientListing>
</ns2:ClientListingConsignment>
"""
            % annual_listing_data
        )

        data_file += data_begin + data_comp + data_client_info + data_end

        file_save = base64.b64encode(data_file.encode("utf8"))
        self.write({"file_save": file_save})

        model_datas = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.ui.view"),
                ("name", "=", "view_vat_listing_result"),
            ],
            limit=1,
        )
        resource_id = model_datas.res_id

        return {
            "name": _("XML File has been Created"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.list",
            "views": [(resource_id, "form")],
            "context": self.env.context,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    @api.multi
    def print_vatlist(self):
        self.ensure_one()

        if not self.partner_ids:
            raise UserError(_("No record to print."))

        return self.env.ref(
            "l10n_be_vat_reports.action_report_l10nvatpartnerlisting"
        ).report_action(self)
