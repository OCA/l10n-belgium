# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountCompanywebConfigSettings(models.TransientModel):
    _name = 'account.companyweb.config.settings'
    _inherit = 'res.config.settings'

    companyweb_login = fields.Char('Login', size=16)
    companyweb_pswd = fields.Char('Password', size=16)
