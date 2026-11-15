# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    cnk_code = fields.Char(help="This is the CNK reference for Belgian pharmaceuticals")

    @property
    def _has_cnk_code_error(self):
        self.ensure_one()
        return bool(self.cnk_code and len(self.cnk_code) != 7)

    @api.constrains("cnk_code")
    def _check_cnk_code(self):
        for product in self:
            if product._has_cnk_code_error:
                raise ValidationError(
                    self.env._(
                        "The product (%(product_name)s) has a wrong CNK Code "
                        "(lenght is not 7)!"
                    )
                )
