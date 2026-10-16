# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class MedipimProductProductRecordHandler(Component):
    """Interact w/ odoo importable records."""

    _name = "medipim.product.product.handler"
    _inherit = "product.product.handler"
    _usage = "medipim.record"

    def odoo_exists(self, values, orig_values):
        """
        We don't want to exclude inactive products as we want to manage them too
        """
        new_self = self
        new_self.work.model = self.model.with_context(active_test=False)
        return super(MedipimProductProductRecordHandler, new_self).odoo_exists(
            values, orig_values
        )

    def odoo_post_create(self, odoo_record, values, orig_values):
        self._update_template_state(odoo_record, values, orig_values)

    def _update_template_state(self, odoo_record, values, orig_values):
        """
        State is on product template side
        """
        if odoo_record.product_tmpl_id.product_variant_ids:
            # We assume we have one variant / one template
            state = values.get("state")
            if state and state != odoo_record.product_tmpl_id.state:
                odoo_record.product_tmpl_id.state = state
