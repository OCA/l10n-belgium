# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, release
from lxml import etree


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'base.ubl']

    # TODO: maybe we will have to switch from UBL 2.1 to UBL 2.0...
    # to be e-fff compliant
    @api.multi
    def _ubl_add_header(self, parent_node, ns):
        '''Add mandatory fields ProfileID + CustomizationID'''
        res = super(AccountInvoice, self)._ubl_add_header(parent_node, ns)
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

    @api.multi
    def get_ubl_filename(self):
        '''Read from http://www.e-fff.be/FR/doc03.php :
        The e-fff community recommends to use the following file naming:
        efff_BE0123456789_AlphaNumericCharactersFreeOfChoice.xml'''
        filename = 'efff_%s_Invoice_%s' % (
            self.commercial_partner_id.sanitized_vat,
            self.number and self.number.replace('/', '-') or 'draft')
        return filename
