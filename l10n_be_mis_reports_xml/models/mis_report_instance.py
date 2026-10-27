# Copyright 2021 Coop IT Easy SC
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    _is_be_vat_declaration = fields.Boolean(
        compute="_compute_is_be_vat_declaration",
    )

    @api.depends("report_id")
    def _compute_is_be_vat_declaration(self):
        mr_template = self.env.ref(
            "l10n_be_mis_reports.mis_report_vat", raise_if_not_found=False
        )
        for instance in self:
            instance._is_be_vat_declaration = bool(
                mr_template and instance.report_id == mr_template
            )

    def export_xml(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "be.vat.declaration.wizard",
            "target": "new",
            "context": {"default_mr_instance_id": self.id},
        }
