# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs
import time
import base64

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class VATIntraClient(models.TransientModel):
    _name = "vat.intra.client"
    _description = "Vat Intra Client"

    seq = fields.Integer("Sequence")
    partner_name = fields.Char("Client Name")
    vatnum = fields.Char("VAT number")
    vat = fields.Char("VAT")
    country = fields.Char("Country")
    intra_code = fields.Char("Intra Code")
    code = fields.Char("Code")
    amount = fields.Float(string="Amount")

    @api.multi
    def to_dict(self):
        return [
            {
                "partner_name": client.partner_name,
                "seq": client.seq,
                "vatnum": client.vatnum,
                "vat": client.vat,
                "country": client.country,
                "amount": client.amount,
                "intra_code": client.intra_code,
                "code": client.code,
            }
            for client in self
        ]


class PartnerVATIntra(models.TransientModel):
    """
    Partner Vat Intra Wizard
    """

    _name = "partner.vat.intra"
    _description = "Partner VAT Intra"

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

    name = fields.Char("File Name", default="vat_intra.xml")
    period_code = fields.Char(
        string="Period Code",
        size=6,
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
    date_start = fields.Date("Start date", required=True)
    date_end = fields.Date("End date", required=True)
    test_xml = fields.Boolean(
        "Test XML file", help="Sets the XML output as test file"
    )
    mand_id = fields.Char(
        "Reference",
        help="Reference given by the Representative of the sending company.",
    )
    msg = fields.Text("File created", readonly=True)
    no_vat = fields.Text(
        "Partner With No VAT",
        readonly=True,
        help="The Partner whose VAT number is not defined and they are not "
        "included in XML File.",
    )
    file_save = fields.Binary("Save File", readonly=True)
    country_ids = fields.Many2many(
        "res.country",
        "vat_country_rel",
        "vat_id",
        "country_id",
        "European Countries",
        default=_get_europe_country,
    )
    comments = fields.Text("Comments")
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
    amount_total = fields.Float(string="Amount Total", compute="_compute_sums")

    @api.multi
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

    @api.multi
    def get_partners(self):
        self.ensure_one()

        query = """
WITH taxes AS
         (SELECT tag_xmlid.name, tagsrel.account_tax_id
          FROM account_tax_account_tag tagsrel
                   INNER JOIN ir_model_data tag_xmlid ON (
                  tag_xmlid.model = 'account.account.tag'
                  AND tagsrel.account_account_tag_id = tag_xmlid.res_id)
          WHERE tag_xmlid.NAME IN %s)
SELECT p.name          As partner_name,
       l.partner_id    AS partner_id,
       p.vat           AS vat,
       t.name          AS intra_code,
       SUM(-l.balance) AS amount
FROM account_move_line l
         INNER JOIN account_move_line_account_tax_rel taxrel
                    ON (taxrel.account_move_line_id = l.id)
         INNER JOIN taxes t ON (taxrel.account_tax_id = t.account_tax_id)
         LEFT JOIN res_partner p ON (l.partner_id = p.id)
WHERE l.date BETWEEN %s AND %s
    AND l.company_id = %s
GROUP BY p.name, l.partner_id, p.vat, intra_code
          """
        tags_xmlids = ("tax_tag_44", "tax_tag_46L", "tax_tag_46T")
        company_id = self.env.user.company_id.id

        self.env.cr.execute(
            query, (tags_xmlids, self.date_start, self.date_end, company_id)
        )

        seq = 0
        clients = self.env["vat.intra.client"].browse()
        for row in self.env.cr.dictfetchall():
            seq += 1
            amount = row["amount"] or 0.0
            code = {
                "tax_tag_44": "S",
                "tax_tag_46L": "L",
                "tax_tag_46T": "T",
            }.get(row["intra_code"], "")
            vat = row.get("vat") or ""

            client_data = {
                "seq": seq,
                "partner_name": row["partner_name"],
                "vat": vat,
                "vatnum": vat[2:].replace(" ", "").upper(),
                "country": vat[:2],
                "intra_code": row["intra_code"],
                "code": code,
                "amount": round(amount, 2),
            }
            client = self.env["vat.intra.client"].create(client_data)
            clients |= client

        self.client_ids = clients

        model_datas = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("name", "=", "view_vat_intra")],
            limit=1,
        )
        resource_id = model_datas.res_id
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

    @api.multi
    def _get_data(self):
        self.ensure_one()

        # company data
        company = self.env.user.company_id
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

    @api.multi
    def create_xml(self):
        """Creates xml that is to be exported and sent to estate for
           partner vat intra.
        :return: Value for next action.
        :rtype: dict
        """
        xml_data = self._get_data()
        month_quarter = xml_data["period"][:2]
        year = xml_data["period"][2:]
        data_file = ""

        # Can't we do this by etree?
        data_head = """<?xml version="1.0" encoding="UTF-8"?>
    <ns2:IntraConsignment
     xmlns="http://www.minfin.fgov.be/InputCommon"
     xmlns:ns2="http://www.minfin.fgov.be/IntraConsignment"
     IntraListingsNbr="1">
        <ns2:Representative>
            <RepresentativeID
                identificationType="NVAT"
                issuedBy="%(issued_by)s">%(vatnum)s</RepresentativeID>
            <Name>%(company_name)s</Name>
            <Street>%(street)s</Street>
            <PostCode>%(post_code)s</PostCode>
            <City>%(city)s</City>
            <CountryCode>%(country)s</CountryCode>
            <EmailAddress>%(email)s</EmailAddress>
            <Phone>%(phone)s</Phone>
        </ns2:Representative>""" % (
            xml_data
        )
        if xml_data["mand_id"]:
            data_head += (
                "\n\t\t<ns2:RepresentativeReference>"
                "%(mand_id)s"
                "</ns2:RepresentativeReference>" % (xml_data)
            )
        data_comp_period = (
            "\n\t\t<ns2:Declarant>\n\t\t\t"
            "<VATNumber>%(vatnum)s</VATNumber>\n\t\t\t"
            "<Name>%(company_name)s</Name>\n\t\t\t"
            "<Street>%(street)s</Street>\n\t\t\t"
            "<PostCode>%(post_code)s</PostCode>\n\t\t\t"
            "<City>%(city)s</City>\n\t\t\t"
            "<CountryCode>%(country)s</CountryCode>\n\t\t\t"
            "<EmailAddress>%(email)s</EmailAddress>\n\t\t\t"
            "<Phone>%(phone)s</Phone>\n\t\t"
            "</ns2:Declarant>" % (xml_data)
        )
        if month_quarter.startswith("3"):
            data_comp_period += (
                "\n\t\t<ns2:Period>\n\t\t\t"
                "<ns2:Quarter>" + month_quarter[1] + "</ns2:Quarter> \n\t\t\t"
                "<ns2:Year>" + year + "</ns2:Year>\n\t\t</ns2:Period>"
            )
        elif month_quarter.startswith("0") and month_quarter.endswith("0"):
            data_comp_period += (
                "\n\t\t<ns2:Period>\n\t\t\t"
                "<ns2:Year>" + year + "</ns2:Year>\n\t\t"
                "</ns2:Period>"
            )
        else:
            data_comp_period += (
                "\n\t\t<ns2:Period>\n\t\t\t"
                "<ns2:Month>" + month_quarter + "</ns2:Month> \n\t\t\t"
                "<ns2:Year>" + year + "</ns2:Year>\n\t\t"
                "</ns2:Period>"
            )

        data_clientinfo = ""
        for client in xml_data["clientlist"]:
            if not client["vatnum"]:
                msg = _("No vat number defined for %s.")
                raise UserError(msg % client["partner_name"])
            data_clientinfo += (
                '\n\t\t<ns2:IntraClient SequenceNumber="%(seq)s">\n\t\t\t'
                '<ns2:CompanyVATNumber issuedBy="%(country)s">%(vatnum)s'
                "</ns2:CompanyVATNumber>\n\t\t\t"
                "<ns2:Code>%(code)s</ns2:Code>\n\t\t\t"
                "<ns2:Amount>%(amount).2f</ns2:Amount>\n\t\t"
                "</ns2:IntraClient>"
            ) % (client)

        data_decl = (
            '\n\t<ns2:IntraListing SequenceNumber="1" '
            'ClientsNbr="%(clientnbr)s" DeclarantReference="%(dnum)s" '
            'AmountSum="%(amountsum).2f">'
        ) % (xml_data)

        data_file += (
            data_head
            + data_decl
            + data_comp_period
            + data_clientinfo
            + "\n\t\t<ns2:Comment>%(comments)s</ns2:Comment>\n\t"
            "</ns2:IntraListing>\n</ns2:IntraConsignment>"
        ) % (xml_data)

        file_save = base64.b64encode(data_file.encode("utf8"))
        self.write({"file_save": file_save})

        model_data = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.ui.view"),
                ("name", "=", "view_vat_intra_save"),
            ],
            limit=1,
        )
        resource_id = model_data.res_id

        return {
            "name": _("Save"),
            "context": self.env.context,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "partner.vat.intra",
            "views": [(resource_id, "form")],
            "view_id": "view_vat_intra_save",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    @api.multi
    def print_vat_intra(self):
        self.ensure_one()

        if not self.client_ids:
            raise UserError(_("No record to print."))

        return self.env.ref(
            "l10n_be_vat_reports.action_report_l10nvatintraprint"
        ).report_action(self)
