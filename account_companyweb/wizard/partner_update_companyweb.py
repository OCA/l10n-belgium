# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2015 BCIM sprl
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

from openerp import models, fields, api, registry
from openerp.exceptions import Warning


class CwebUpdate(models.TransientModel):
    _name = 'res.partner.cwebupdate'

    count = fields.Integer('Count', readonly=True)

    @api.model
    def default_get(self, fields):
        """
        Use active_ids from the context to fetch the count of clients.
        """
        record_ids = self._context.get('active_ids', [])
        res = super(CwebUpdate, self).default_get(fields)
        partner_env = self.env['res.partner']
        partners = partner_env.search(
            [('is_company', '=', True),
             ('id', 'in', record_ids),
             ('vat', '!=', False)])
        res['count'] = len(partners)
        return res

    @api.one
    def action_update(self):
        record_ids = self._context.get('active_ids', [])

        # We create a new cursor to ensure we do not loose data already retrieved
        with registry(self.env.cr.dbname).cursor() as new_cr:
            uid, context = self.env.uid, self.env.context
            partner_env = api.Environment(new_cr, uid, context)['res.partner']
            partners = partner_env.search(
                [('is_company', '=', True),
                 ('id', 'in', record_ids),
                 ('vat', '!=', False)])
            for partner in partners:
                try:
                    partner._cweb_refresh(force_update=not partner.cweb_lastupdate)
                    new_cr.commit()
                except Warning:
                    pass
        return {}
