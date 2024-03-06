# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SC

from odoo import fields, models


# todo: use common class for common fields and logic with
# partner.vat.list.client: seq, name, vatnum, country,...
class VATIntraClient(models.TransientModel):
    _name = "vat.intra.client"
    _description = "Vat Intra Client"

    seq = fields.Integer("Sequence")
    partner_name = fields.Char("Client Name")
    vatnum = fields.Char("VAT number")
    vat = fields.Char("VAT")
    country = fields.Char()
    intra_code = fields.Char()
    code = fields.Char()
    amount = fields.Float()
