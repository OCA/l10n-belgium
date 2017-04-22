# -*- coding: utf-8 -*-
# ©  2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import re
from odoo import api, models


class ResPartnerIdCategory(models.Model):
    _inherit = "res.partner.id_category"

    @api.model
    def validate_l10n_be_id_card(self, id_number):
        """Method called from the validation_code to validate a belgium id
        card number
        """
        # replace all non digit char since on an identity card, the number is
        # formatted as 000-00000000-97
        num = re.sub('[^0-9]', '', id_number.name)
        failed = True
        if len(num) != 12:
            return failed
        if not num.isdigit():
            return failed
        prefix = int(num[0:10])
        suffix = int(num[-2:])
        to_check = 97 - (prefix % 97)

        if (to_check == 97 and to_check == suffix) or\
                (int(suffix) + int(to_check) == 97):
            return not failed
        else:
            return failed
