from odoo import api, fields, models

# Copyright 2023 ACSONE SA/NV


class ResPartner(models.Model):

    _inherit = "res.partner"

    is_belgian_address = fields.Boolean("Is it a Belgian address ?")

    @api.onchange("is_belgian_address")
    def _onchange_is_belgian_address(self):
        belgium = self.env.ref("base.be")
        for rec in self:
            if rec.is_belgian_address:
                rec.country_id = belgium
            else:
                rec.country_id = ""
