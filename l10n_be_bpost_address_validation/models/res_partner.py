# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_be = fields.Boolean(compute="_compute_is_be")

    @api.depends("country_id")
    def _compute_is_be(self):
        for rec in self:
            if rec.country_id.code == "BE":
                rec.is_be = True
            else:
                rec.is_be = False

    def action_check_address_validity(self):
        return {
            "name": _("Check Address Validity"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "bpost.address.validation.wizard",
            "target": "new",
            "context": {"default_partner_id": self.ids[0]},
        }
