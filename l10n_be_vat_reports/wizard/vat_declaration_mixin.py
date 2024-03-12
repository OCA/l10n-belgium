# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VATDeclarationMixin(models.AbstractModel):
    _name = "vat.declaration.mixin"
    _description = "VAT Declaration Mixin"

    def _compute_declarant_partner_id(self):
        company = self.env.company
        partner_id = company.partner_id.address_get(["invoice"]).get("invoice")
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
        else:
            partner = company.partner_id
        for declaration in self:
            declaration.declarant_partner_id = partner

    def _compute_declarant_vat(self):
        company = self.env.company
        # remove any non-digit character
        declarant_vat = re.sub(r"\D", "", company.vat)
        for rec in self:
            rec.declarant_vat = declarant_vat

    @api.depends("declarant_partner_id")
    def _compute_declarant_phone(self):
        for rec in self:
            phone = rec.declarant_partner_id.phone
            if phone:
                starts_with_plus = phone.strip().startswith("+")
                # remove any non-digit character
                phone = re.sub(r"\D", "", phone)
                if starts_with_plus:
                    phone = "+" + phone
            if not phone:
                phone = False
            rec.declarant_phone = phone

    @api.depends("declarant_vat")
    def _compute_declarant_reference(self):
        self.env["ir.sequence"].next_by_code("declarantnum")
        for rec in self:
            declarant_vat = rec.declarant_vat
            if not declarant_vat:
                raise ValidationError(_("No VAT number associated with your company."))
            seq_declarantnum = self.env["ir.sequence"].next_by_code("declarantnum")
            rec.declarant_reference = declarant_vat + seq_declarantnum[-4:]

    declarant_partner_id = fields.Many2one(
        "res.partner", "Declarant partner", compute=_compute_declarant_partner_id
    )
    declarant_vat = fields.Char(
        string="Declarant Tax ID",
        compute="_compute_declarant_vat",
    )
    declarant_phone = fields.Char(
        compute="_compute_declarant_phone",
    )
    declarant_reference = fields.Char(compute=_compute_declarant_reference)
    comments = fields.Text()
