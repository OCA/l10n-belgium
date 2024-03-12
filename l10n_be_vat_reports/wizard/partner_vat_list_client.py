# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SC
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VATListingClients(models.TransientModel):
    _name = "partner.vat.list.client"
    _description = "Partner VAT List Clients"

    seq = fields.Integer("Sequence")
    name = fields.Char("Client Name", help="Used as file name.")
    vat = fields.Char("VAT")
    turnover = fields.Float("Base Amount")
    vat_amount = fields.Float("VAT Amount")

    @api.constrains("vat")
    def _check_vat_number(self):
        """
        Belgium VAT numbers must respect this pattern: [0-1][0-9]{9}
        todo current code assumes vat numbers start with a two-letter
          country code
        """
        be_vat_pattern = re.compile(r"^BE[0-1][0-9]{9}$")
        for client in self:
            if not be_vat_pattern.match(client.vat):
                raise ValidationError(
                    _(  # pylint: disable=W8120 because '{9}' triggers error
                        "Belgian Intervat platform only accepts VAT numbers "
                        "matching this pattern: [0-1][0-9]{9} (number "
                        "part). Check vat number %(vat)s for client %(vat)s"
                    )
                    % {
                        "vat": client.vat,
                        "name": client.name,
                    }
                )
