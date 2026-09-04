# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cnk_code = fields.Char(
        compute="_compute_cnk_code",
        inverse="_inverse_cnk_code",
        search="_search_cnk_code",
        help="This is the CNK reference for Belgian pharmaceuticals",
    )

    @api.depends("product_variant_ids.cnk_code")
    def _compute_cnk_code(self):
        self._compute_template_field_from_variant_field("cnk_code")

    def _inverse_cnk_code(self):
        self._set_product_variant_field("cnk_code")

    def _search_cnk_code(self, operator, value):
        subquery = self.with_context(active_test=False)._search(
            [
                ("product_variant_ids.cnk_code", operator, value),
            ]
        )
        return [("id", "in", subquery)]
