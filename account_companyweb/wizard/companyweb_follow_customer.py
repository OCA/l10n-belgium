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


class CompanywebFollowCustomer(models.TransientModel):
    _name = 'companyweb.follow.customer'

    count = fields.Integer('Count', readonly=True)
    count_ignored = fields.Integer('Ignored', readonly=True)

    @api.model
    def default_get(self, fields):
        """
        Use active_ids from the context to fetch the count of clients.
        """
        result = super(CompanywebFollowCustomer, self).default_get(fields)

        record_ids = self._context.get('active_ids', [])
        partner_env = self.env['res.partner']
        partners = partner_env.search(
            [('is_company', '=', True),
             ('id', 'in', record_ids),
             ('vat', '!=', False),
             ('cweb_follow_customer', '=', False)])

        count_ignored = len(record_ids) - len(partners)

        result.update({
            'count': len(partners),
            'count_ignored': count_ignored
        })

        return result

    @api.multi
    def action_add(self):
        self.ensure_one()

        record_ids = self._context.get('active_ids', [])
        partner_env = self.env['res.partner']
        partners = partner_env.search(
            [('is_company', '=', True),
             ('id', 'in', record_ids),
             ('vat', '!=', False),
             ('cweb_follow_customer', '=', False)])

        if not partners:
            raise Warning('Please select at least one customer')

        partners.add_customer_to_companyvat()
