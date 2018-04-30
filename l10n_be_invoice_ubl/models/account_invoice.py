# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, release
from lxml import etree


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def get_ubl_version(self):
        '''e-fff is based on UBL 2.0, not UBL 2.1'''
        return '2.0'

    def _ubl_add_header(self, parent_node, ns, version='2.1'):
        '''Add mandatory fields ProfileID + CustomizationID'''
        res = super(AccountInvoice, self)._ubl_add_header(
            parent_node, ns, version=version)
        namespaces = parent_node.nsmap
        namespaces.pop(None)
        version_node_find = parent_node.find(
            './/cbc:UBLVersionID', namespaces=namespaces)
        customization_id = etree.Element(ns['cbc'] + 'CustomizationID')
        customization_id.text = '1.0'
        parent_node.insert(
            parent_node.index(version_node_find) + 1, customization_id)
        profile_id = etree.Element(ns['cbc'] + 'ProfileID')
        profile_id.text = 'EFFF.BE Odoo %s' % release.version
        parent_node.insert(
            parent_node.index(version_node_find) + 2, profile_id)
        return res

    def get_ubl_filename(self, version='2.1'):
        '''Read from http://www.e-fff.be/FR/doc03.php :
        The e-fff community recommends to use the following file naming:
        efff_BE0123456789_AlphaNumericCharactersFreeOfChoice.xml'''
        filename = 'efff_%s_Invoice_%s.xml' % (
            self.commercial_partner_id.sanitized_vat or '',
            self.number and self.number.replace('/', '-') or 'draft')
        return filename
