# -*- coding: utf-8 -*-
# ©  2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import re
from openerp import api, models


class ResPartnerIdCategory(models.Model):
    _inherit = "res.partner.id_category"

    @api.model
    def validate_l10n_be_national_registry_number(self, id_number):
        """Method called from the validation_code to validate a belgium
        `Wikipedia
         <https://fr.wikipedia.org/wiki/Num%C3%A9ro_de_registre_national>`_
         The method doesn't support number for persons more than 100 years old.
        """
        # replace all non digit char since on an identity card, the number is
        # formatted as 85.01.01-002.00
        num = re.sub('[^0-9]', '', id_number.name)
        failed = True
        if len(num) != 11:
            return failed
        if not num.isdigit():
            return failed
        seq = int(num[0:9])
        YY = num[:2]
        pivot_YY = datetime.date.today().year - 2000
        if YY <= pivot_YY:
            # the person is born after 31/12/1999
            seq = seq + 2000000000
        check = int(num[9:])
        to_check = 97 - (seq % 97)
        if check == 97 and to_check == 0:
            return not failed
        if to_check != check:
            return failed
        return not failed
