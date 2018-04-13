# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.report.models import report

from lxml.etree import XML
import unittest

from .common import TestVatReportsCommon


class TestVatListing(TestVatReportsCommon):

    def setUp(self):
        super(TestVatReportsCommon, self).setUp()
        company = self.env.user.company_id
        tax = self.env.ref('l10n_be.%s_attn_VAT-OUT-21-S' % company.id)
        self._create_test_data(tax)

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
