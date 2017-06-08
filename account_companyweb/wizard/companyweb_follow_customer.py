# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# Copyright (c) 2017 Okia SPRL (https://okia.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


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
             ('vat', 'ilike', 'be%'),
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
             ('vat', 'ilike', 'be%'),
             ('cweb_follow_customer', '=', False)])

        if not partners:
            raise UserError(_('Please select at least one customer'))

        partners.add_customer_to_companyvat()
