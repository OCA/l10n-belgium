# Copyright 2004-2010 Tiny SPRL
# Copyright 2018 ACSONE SA/NV
# Copyright 2020 Coop IT Easy SCRLfs
import re

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VATListingClients(models.TransientModel):
    _name = "partner.vat.list.client"
    _description = "Partner VAT List Clients"

    seq = fields.Integer("Sequence")
    name = fields.Char("Client Name", help="Used as file name.")
    vat = fields.Char("VAT")
    turnover = fields.Float("Base Amount")
    vat_amount = fields.Float("VAT Amount")

    @api.multi
    @api.constrains("vat")
    def _check_vat_number(self):
        """
        Belgium VAT numbers must respect this pattern: 0[1-9]{1}[0-9]{8}
        todo current code assumes vat numbers start with a two-letter
          country code
        """
        be_vat_pattern = re.compile(r"^BE0[1-9]{1}[0-9]{8}$")
        for client in self:
            if not be_vat_pattern.match(client.vat):
                raise ValidationError(
                    _(
                        "Belgian Intervat platform only accepts VAT numbers "
                        "matching this pattern: 0[1-9]{1}[0-9]{8} (number "
                        "part). Check vat number %s for client %s"
                    )
                    % (client.vat, client.name)
                )
