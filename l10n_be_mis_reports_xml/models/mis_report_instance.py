# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    _is_be_vat_declaration = fields.Boolean(
        compute="_compute_is_be_vat_declaration"
    )

    @api.multi
    def _compute_is_be_vat_declaration(self):
        mr_template = self.env.ref("l10n_be_mis_reports.mis_report_vat")
        for instance in self:
            instance._is_be_vat_declaration = (
                instance.report_id == mr_template
            )

    def export_xml(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "be.vat.declaration.wizard",
            "target": "new",
        }
