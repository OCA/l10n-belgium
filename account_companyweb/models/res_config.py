# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models
from openerp import SUPERUSER_ID


_parameters = {
    "companyweb.login": "",
    "companyweb.pswd": "",
}


class AccountCompanywebConfigSettings(models.TransientModel):
    _name = 'account.companyweb.config.settings'
    _inherit = 'res.config.settings'

    companyweb_login = fields.Char('Login', 16),
    companyweb_pswd = fields.Char('Password', 16),

    def init(self, cr, force=False):
        config_parameter_model = self.pool['ir.config_parameter']
        for key, value in _parameters.iteritems():
            ids = not force and config_parameter_model.search(
                cr, SUPERUSER_ID, [('key', '=', key)])
            if not ids:
                config_parameter_model.set_param(cr, SUPERUSER_ID, key, value)

    def get_default_companyweb_login(self, cr, uid, fields_name, context=None):
        login = self.pool['ir.config_parameter'].get_param(
            cr, SUPERUSER_ID, 'companyweb.login', False)
        return {'companyweb_login': login}

    def get_default_companyweb_pswd(self, cr, uid, fields_name, context=None):
        pswd = self.pool['ir.config_parameter'].get_param(
            cr, SUPERUSER_ID, 'companyweb.pswd', False)
        return {'companyweb_pswd': pswd}

    def set_default_companyweb_login(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        self.pool['ir.config_parameter'].set_param(
            cr, SUPERUSER_ID, 'companyweb.login', config.companyweb_login)
        return True

    def set_default_companyweb_pswd(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        self.pool['ir.config_parameter'].set_param(
            cr, SUPERUSER_ID, 'companyweb.pswd', config.companyweb_pswd)
        return True
