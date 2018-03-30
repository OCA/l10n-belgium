# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.addons.report.models import report

from lxml.etree import XML
import unittest


class TestVatReports(TransactionCase):

    def setUp(self):
        super(TestVatReports, self).setUp()
        chart = self.env.ref('l10n_be.l10nbe_chart_template')
        chart.try_loading_for_current_company()
        company = self.env.user.company_id
        company.partner_id.write({'vat': 'PT999999990'})
        tax = self.env.ref('l10n_be.%s_attn_VAT-OUT-21-S' % company.id)
        self.partner = self.env.ref('base.res_partner_12')
        self.partner.write({'vat': 'BE0477472701'})
        account_rcv = self.partner.property_account_receivable_id
        account_rev_type = self.env.ref('account.data_account_type_revenue')
        account_line = self.env['account.account'].search([
            ('user_type_id', '=', account_rev_type.id)
        ], limit=1)
        invoice = self.env['account.invoice'].create({
            'company_id': company.id,
            'currency_id': self.env.ref('base.EUR').id,
            'account_id': account_rcv.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Computer SC234',
                'price_unit': 450.0,
                'quantity': 1.0,
                'product_id': self.env.ref('product.product_product_3').id,
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'invoice_line_tax_ids': [(6, 0, [tax.id])],
                'account_id': account_line.id,
            })],
            'partner_id': self.partner.id,
        })
        invoice.action_invoice_open()

    def _prepare_listing(self):
        wizard = self.env['partner.vat'].create({
            'year': '2018',
            'limit_amount': 1,
        })
        action = wizard.get_partner()
        vat_listings_ids = action['context']['partner_ids']
        vat_listings = self.env['vat.listing.clients'].browse(vat_listings_ids)
        vat_listing = next(vl for vl in vat_listings
                           if vl.vat == self.partner.vat)
        self.assertEqual(94.5, vat_listing.vat_amount)
        context = dict(
            self.env.context,
            partner_ids=[vat_listing.id],
            year='2018',
            limit_amount=1,
        )
        full_list = self.env['partner.vat.list'].with_context(
            context).create({})
        return full_list

    def test_xml_list(self):
        full_list = self._prepare_listing()
        full_list.create_xml()
        ns = {'ns2': 'http://www.minfin.fgov.be/ClientListingConsignment'}
        xml = XML(full_list.file_save.decode('base64'))
        xml_vat_amount = xml.xpath(
            '//ns2:Client[ns2:CompanyVATNumber[text() = "0477472701"]]'
            '/ns2:VATAmount',
            namespaces=ns)[0].text
        self.assertEqual('94.50', xml_vat_amount)

    @unittest.skipIf(report.wkhtmltopdf_state == 'install',
                     'wkhtmltopdf not available')
    def test_pdf_list(self):
        full_list = self._prepare_listing()
        report_action = full_list.print_vatlist()
        context = full_list.env.context
        self.env['report'].with_context(context).get_pdf(
            [], report_action['report_name'], data=report_action['data'])
