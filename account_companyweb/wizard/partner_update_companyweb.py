# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, registry
from openerp.exceptions import Warning as UserError


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

    @api.multi
    def action_update(self):
        self.ensure_one()

        record_ids = self._context.get('active_ids', [])

        # We create a new cursor to ensure we do not loose data already
        # retrieved
        with registry(self.env.cr.dbname).cursor() as new_cr:
            uid, context = self.env.uid, self.env.context
            partner_env = api.Environment(new_cr, uid, context)['res.partner']
            partners = partner_env.search(
                [('is_company', '=', True),
                 ('id', 'in', record_ids),
                 ('vat', '!=', False)])
            for partner in partners:
                try:
                    partner._cweb_refresh(
                        force_update=not partner.cweb_lastupdate)
                    new_cr.commit()
                except UserError:
                    pass
        return {}
