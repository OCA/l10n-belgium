# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 ACSONE SA/NV (<http://acsone.eu>)
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Adapted by Noviat to
#     - make the 'mand_id' field optional
#     - support Noviat tax code scheme
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import base64

from openerp import api, models, fields, _
from openerp.report import report_sxw
from openerp.exceptions import Warning as UserError


class PartnerVATIntra(models.TransientModel):
    """
    Partner Vat Intra
    """
    _name = "partner.vat.intra"
    _description = 'Partner VAT Intra'

    @api.model
    def _get_europe_country(self):
        return self.env['res.country'].search([
            ('code', 'in', ['AT', 'BG', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                            'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
                            'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES',
                            'SE', 'GB'])
        ])

    name = fields.Char('File Name', default='vat_intra.xml')
    period_code = fields.Char(
        string='Period Code', size=6, required=True,
        help='''This is where you have to set the period code for the '''
             '''intracom declaration using the format: ppyyyy
          PP can stand for a month: from '01' to '12'.
          PP can stand for a trimester: '31','32','33','34'
              The first figure means that it is a trimester
              The second figure identify the trimester.
          PP can stand for a complete fiscal year: '00'.
          YYYY stands for the year (4 positions).'''
    )
    date_start = fields.Date('Start date', required=True)
    date_end = fields.Date('End date', required=True)
    test_xml = fields.Boolean(
        'Test XML file', help="Sets the XML output as test file")
    mand_id = fields.Char(
        'Reference',
        help="Reference given by the Representative of the sending company.")
    msg = fields.Text('File created', readonly=True)
    no_vat = fields.Text(
        'Partner With No VAT', readonly=True,
        help="The Partner whose VAT number is not defined and they are not "
             "included in XML File.")
    file_save = fields.Binary(
        'Save File', readonly=True)
    country_ids = fields.Many2many(
        'res.country', 'vat_country_rel', 'vat_id', 'country_id',
        'European Countries', default=_get_europe_country)
    comments = fields.Text('Comments')

    @api.multi
    def _get_datas(self):
        """Collects require data for vat intra xml
        :param ids: id of wizard.
        :return: dict of all data to be used to generate xml for
                 Partner VAT Intra.
        :rtype: dict
        """
        self.ensure_one()

        obj_sequence = self.env['ir.sequence']
        obj_partner = self.env['res.partner']

        xmldict = {}
        post_code = street = city = country = ''
        seq = amount_sum = 0

        wiz_data = self
        comments = wiz_data.comments

        data_company = self.env.user.company_id

        # Get Company vat
        company_vat = data_company.partner_id.vat
        if not company_vat:
            raise UserError(_('No VAT number associated with your company.'))
        company_vat = company_vat.replace(' ', '').upper()
        issued_by = company_vat[:2]

        if len(wiz_data.period_code) != 6:
            raise UserError(_('Period code is not valid.'))

        if not wiz_data.date_start <= wiz_data.date_end:
            raise UserError(_('Start date cannot be after the end date.'))

        p_id_list = obj_partner.search([('vat', '!=', False)])
        if not p_id_list:
            raise UserError(
                _('No partner has a VAT number associated with him.'))

        seq_declarantnum = obj_sequence.next_by_code('declarantnum')
        dnum = company_vat[2:] + seq_declarantnum[-4:]

        addr = data_company.partner_id.address_get(['invoice'])
        email = data_company.partner_id.email or ''
        phone = data_company.partner_id.phone or ''

        if addr.get('invoice', False):
            ads = obj_partner.browse([addr['invoice']])
            city = (ads.city or '')
            post_code = (ads.zip or '')
            if ads.street:
                street = ads.street
            if ads.street2:
                street += ' '
                street += ads.street2
            if ads.country_id:
                country = ads.country_id.code

        if not country:
            country = company_vat[:2]
        if not email:
            raise UserError(_('No email address associated with the company.'))
        if not phone:
            raise UserError(_('No phone associated with the company.'))
        phone = phone.replace('/', '')\
                     .replace('.', '')\
                     .replace('(', '')\
                     .replace(')', '')\
                     .replace(' ', '')
        xmldict.update({
            'company_name': data_company.name,
            'company_vat': company_vat,
            'vatnum':  company_vat[2:],
            'mand_id': wiz_data.mand_id,
            'sender_date': str(time.strftime('%Y-%m-%d')),
            'street': street,
            'city': city,
            'post_code': post_code,
            'country': country,
            'email': email,
            'phone': phone,
            'period': wiz_data.period_code,
            'clientlist': [],
            'comments': comments,
            'issued_by': issued_by,
        })
        # tax code 44: services
        # tax code 46L: normal good deliveries
        # tax code 46T: ABC good deliveries
        # tax code 48xxx: credite note on tax code xxx
        tags_xmlids = (
            'tax_tag_44',
            'tax_tag_46L',
            'tax_tag_46T',
        )
        self.env.cr.execute('''
WITH taxes AS
  (SELECT tag_xmlid.name, tagsrel.account_tax_id
   FROM account_tax_account_tag tagsrel
   INNER JOIN ir_model_data tag_xmlid ON (
       tag_xmlid.model = 'account.account.tag'
       AND tagsrel.account_account_tag_id = tag_xmlid.res_id)
   WHERE tag_xmlid.NAME IN %s)
          SELECT p.name As partner_name,
                 l.partner_id AS partner_id, p.vat AS vat,
          t.name AS intra_code,
          SUM(-l.balance) AS amount
          FROM account_move_line l
          INNER JOIN account_move_line_account_tax_rel taxrel
            ON (taxrel.account_move_line_id = l.id)
          INNER JOIN taxes t ON (taxrel.account_tax_id = t.account_tax_id)
          LEFT JOIN res_partner p ON (l.partner_id = p.id)
          WHERE l.date BETWEEN %s AND %s
           AND l.company_id = %s
          GROUP BY p.name, l.partner_id, p.vat, intra_code''',
                            (tags_xmlids, wiz_data.date_start,
                             wiz_data.date_end, data_company.id))

        p_count = 0

        for row in self.env.cr.dictfetchall():
            if not row['vat']:
                row['vat'] = ''
                p_count += 1

            seq += 1
            amt = row['amount'] or 0.0
            amount_sum += amt

            intra_code = {
                'tax_tag_44': 'S',
                'tax_tag_46L': 'L',
                'tax_tag_46T': 'T',
            }.get(row['intra_code'], '')

            xmldict['clientlist'].append({
                'partner_name': row['partner_name'],
                'seq': seq,
                'vatnum': row['vat'][2:].replace(' ', '').upper(),
                'vat': row['vat'],
                'country': row['vat'][:2],
                'amount': round(amt, 2),
                'intra_code': row['intra_code'],
                'code': intra_code,
            })

        xmldict.update({
            'dnum': dnum,
            'clientnbr': str(seq),
            'amountsum': round(amount_sum, 2),
            'partner_wo_vat': p_count,
        })
        return xmldict

    @api.multi
    def create_xml(self):
        """Creates xml that is to be exported and sent to estate for
           partner vat intra.
        :return: Value for next action.
        :rtype: dict
        """
        mod_obj = self.env['ir.model.data']
        xml_data = self._get_datas()
        month_quarter = xml_data['period'][:2]
        year = xml_data['period'][2:]
        data_file = ''

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
    </ns2:Representative>""" % (xml_data)
        if xml_data['mand_id']:
            data_head += '\n\t\t<ns2:RepresentativeReference>'\
                         '%(mand_id)s'\
                         '</ns2:RepresentativeReference>' % (xml_data)
        data_comp_period = '\n\t\t<ns2:Declarant>\n\t\t\t'\
                           '<VATNumber>%(vatnum)s</VATNumber>\n\t\t\t'\
                           '<Name>%(company_name)s</Name>\n\t\t\t'\
                           '<Street>%(street)s</Street>\n\t\t\t'\
                           '<PostCode>%(post_code)s</PostCode>\n\t\t\t'\
                           '<City>%(city)s</City>\n\t\t\t'\
                           '<CountryCode>%(country)s</CountryCode>\n\t\t\t'\
                           '<EmailAddress>%(email)s</EmailAddress>\n\t\t\t'\
                           '<Phone>%(phone)s</Phone>\n\t\t'\
                           '</ns2:Declarant>' % (xml_data)
        if month_quarter.startswith('3'):
            data_comp_period += (
                '\n\t\t<ns2:Period>\n\t\t\t'
                '<ns2:Quarter>'+month_quarter[1]+'</ns2:Quarter> \n\t\t\t'
                '<ns2:Year>'+year+'</ns2:Year>\n\t\t</ns2:Period>')
        elif month_quarter.startswith('0') and month_quarter.endswith('0'):
            data_comp_period += (
                '\n\t\t<ns2:Period>\n\t\t\t'
                '<ns2:Year>'+year+'</ns2:Year>\n\t\t'
                '</ns2:Period>')
        else:
            data_comp_period += (
                '\n\t\t<ns2:Period>\n\t\t\t'
                '<ns2:Month>'+month_quarter+'</ns2:Month> \n\t\t\t'
                '<ns2:Year>'+year+'</ns2:Year>\n\t\t'
                '</ns2:Period>')

        data_clientinfo = ''
        for client in xml_data['clientlist']:
            if not client['vatnum']:
                msg = _('No vat number defined for %s.')
                raise UserError(msg % client['partner_name'])
            data_clientinfo += (
                '\n\t\t<ns2:IntraClient SequenceNumber="%(seq)s">\n\t\t\t'
                '<ns2:CompanyVATNumber issuedBy="%(country)s">%(vatnum)s'
                '</ns2:CompanyVATNumber>\n\t\t\t'
                '<ns2:Code>%(code)s</ns2:Code>\n\t\t\t'
                '<ns2:Amount>%(amount).2f</ns2:Amount>\n\t\t'
                '</ns2:IntraClient>') % (client)

        data_decl = (
            '\n\t<ns2:IntraListing SequenceNumber="1" '
            'ClientsNbr="%(clientnbr)s" DeclarantReference="%(dnum)s" '
            'AmountSum="%(amountsum).2f">') % (xml_data)

        data_file += (
            data_head + data_decl + data_comp_period + data_clientinfo +
            '\n\t\t<ns2:Comment>%(comments)s</ns2:Comment>\n\t'
            '</ns2:IntraListing>\n</ns2:IntraConsignment>') % (xml_data)
        self.write({'file_save': base64.b64encode(data_file.encode('utf-8'))})

        model_data = mod_obj.search([
            ('model', '=', 'ir.ui.view'),
            ('name', '=', 'view_vat_intra_save')
        ], limit=1)
        resource_id = model_data.res_id

        return {
            'name': _('Save'),
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'partner.vat.intra',
            'views': [(resource_id, 'form')],
            'view_id': 'view_vat_intra_save',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def preview(self):
        xml_data = self._get_datas()
        datas = {
            'ids': [],
            'model': 'partner.vat.intra',
            'form': xml_data
        }
        empty = self.env['partner.vat.intra']
        return self.env['report'].get_action(
            empty, 'l10n_be_vat_reports.report_l10nvatintraprint', data=datas)


class WrappedVATIntraPrint(models.AbstractModel):
    _name = 'report.l10n_be_vat_reports.report_l10nvatintraprint'
    _inherit = 'report.abstract_report'
    _template = 'l10n_be_vat_reports.report_l10nvatintraprint'
    _wrapped_report_class = report_sxw.rml_parse
