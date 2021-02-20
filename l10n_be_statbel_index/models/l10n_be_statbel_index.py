# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class L10nBeStatbelIndex(models.Model):

    _name = "l10n_be.statbel.index"
    _description = "StatBel Index"
    _order = "year desc, month desc"

    month = fields.Char(
        required=True,
    )
    year = fields.Char(
        required=True,
    )
    display_date = fields.Char(
        compute="_compute_display_date",
        store=True,
        index=True,
    )
    base_year = fields.Char(
        required=True,
        index=True,
    )
    index_type = fields.Selection(
        selection=lambda self: self._get_index_type(),
        required=True,
        index=True,
    )
    index_value = fields.Float()

    _sql_constraints = [
        (
            "entry_uniq",
            "unique(month, year, base_year, index_type)",
            "Index should be unique per month/year and per base year!",
        ),
    ]

    @api.model
    def _format_date(self, month, year):
        return "{month}/{year}".format(month=month, year=year)

    def _get_index_type(self):
        return [
            ("consumer_index", "Consumer Index"),
            ("consumer_index_wo_ene", "Consumer Index Without Energetic Products"),
            ("consumer_index_wo_ptrl", "Consumer Index Without Petroleum Products"),
            ("inflation", "Inflation"),
            ("health_index", "Health Index"),
            ("smooth_health_index", "Smooth Health Index"),
        ]

    @api.depends("display_date", "base_year")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{display_date} ({base_year})".format(
                display_date=record.display_date,
                base_year=record.base_year,
            )

    @api.depends("month", "year")
    def _compute_display_date(self):
        for record in self:
            record.display_date = self._format_date(record.month, record.year)

    @api.model
    def cron_retrieve(self):
        wizard = self.env["l10n_be.statbel.retrieval"].create({})
        wizard.retrieve_statbel()
