# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models

SUPERUSER_ID = 1

_parameters = {
    "companyweb.login": "",
    "companyweb.pswd": "",
}


class account_companyweb_config_settings(models.TransientModel):
    _name = 'account.companyweb.config.settings'
    _inherit = 'res.config.settings'

    companyweb_login = fields.Char('Login')
    companyweb_pswd = fields.Char('Password')

    def init(self, force=False):
        config_parameter_model = self.env['ir.config_parameter']
        for key, value in _parameters.iteritems():
            ids = not force and config_parameter_model.search(
                [('key', '=', key)])
            if not ids:
                config_parameter_model.set_param(key, value)

    def get_default_companyweb_login(self, fields_name):
        login = self.env['ir.config_parameter'].get_param('companyweb.login', False)
        return {'companyweb_login': login}

    def get_default_companyweb_pswd(self, fields_name):
        pswd = self.env['ir.config_parameter'].get_param(
            'companyweb.pswd', False)
        return {'companyweb_pswd': pswd}

    def set_default_companyweb_login(self):
        ctx = self.env.context
        config = self
        self.env['ir.config_parameter'].set_param(
            'companyweb.login', config.companyweb_login)
        return True

    def set_default_companyweb_pswd(self):
        config = self
        self.env['ir.config_parameter'].set_param(
            'companyweb.pswd', config.companyweb_pswd)
        return True
