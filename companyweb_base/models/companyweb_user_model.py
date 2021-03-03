# -*- coding: utf-8 -*-
# Copyright 2021-2023 ACSONE SA/NV
from odoo import api, fields, models

#
# Extension of ref_user to store identification information
# this is mandatory for API CALL
# If empty the user will be prompted with a wizard to give his credentials


class CompanyWebUser(models.Model):
    _inherit = 'res.users'
    cweb_login = fields.Char('Company Web Login')
    cweb_password = fields.Char('Company Web Password')
