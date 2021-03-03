# -*- coding: utf-8 -*-
# Copyright 2021-2023 ACSONE SA/NV
from odoo import api, fields, models, exceptions


class CompanyWebUserWizard(models.TransientModel):

    _name = 'companyweb_base.user_wizard'
    _description = 'Ask for CompanyWeb login & password'
    cweb_login = fields.Char('Company Web Login')
    cweb_password = fields.Char('Company Web Password')

    def get_credentials(self):
        self.ensure_one()
        if not (self.cweb_login or self.cweb_password):
            raise exceptions.ValidationError('No input given')
        self.env.user.cweb_login = self.cweb_login
        self.env.user.cweb_password = self.cweb_password
        self.env['res.partner'].browse(self.env.context['active_id']).button_companyweb()
