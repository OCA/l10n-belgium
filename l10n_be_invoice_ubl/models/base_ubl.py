# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from lxml import etree


class BaseUbl(models.AbstractModel):
    _inherit = 'base.ubl'

    @api.model
    def _ubl_add_party_identification(
            self, commercial_partner, parent_node, ns, version='2.1'):
        res = super(BaseUbl, self)._ubl_add_party_identification(
            commercial_partner, parent_node, ns, version=version)
        if (
                commercial_partner.sanitized_vat and
                commercial_partner.sanitized_vat.startswith('BE')):
            party_ident = etree.SubElement(
                parent_node, ns['cac'] + 'PartyIdentification')
            party_ident_id = etree.SubElement(
                party_ident, ns['cbc'] + 'ID',
                schemeAgencyID='BE', schemeAgencyName='KBO',
                schemeURI='http://www.FFF.be/KBO')
            party_ident_id.text = commercial_partner.sanitized_vat[2:]
        return res
