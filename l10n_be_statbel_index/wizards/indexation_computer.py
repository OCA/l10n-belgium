# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models
from odoo.fields import first


class StatBelIndexationComputer(models.TransientModel):

    _name = "l10n_be.statbel.indexation.computer"
    _description = "Wizard to compute indexation"

    contract_date = fields.Date(
        required=True, help="The date at which the contract was signed."
    )
    into_force_date = fields.Date(
        help="The date at which the contract has come into force."
    )
    compute_date = fields.Date(
        required=True, help="The date for which we compute the indexation."
    )
    base_year = fields.Char(
        compute="_compute_base_year",
        help="The index base year depending on indexes values (1914, 1936, ...)",
    )
    reference_month = fields.Char(
        compute="_compute_reference_month",
        help="The month reference that helps to get the original index value.",
    )
    reference_index_id = fields.Many2one(
        compute="_compute_base_year",
        comodel_name="l10n_be.statbel.index",
    )
    actual_index_id = fields.Many2one(
        compute="_compute_price",
        comodel_name="l10n_be.statbel.index",
    )
    original_price = fields.Float(
        digits="Product Price",
        required=True,
    )
    computed_price = fields.Float(
        digits="Product Price",
        compute="_compute_price",
    )
    computed_formula = fields.Char(compute="_compute_price")
    region = fields.Selection(
        selection=[
            ("brussels", "Brussels Region"),
            ("flemish", "Flemish Region"),
            ("walloon", "Waloon Region"),
        ],
        required=True,
    )

    def _get_formula_string(self):
        """The formula string that represents the computation for new index"""
        return "{price} * ({actual_index} / {original_index})".format(
            price=self.original_price,
            actual_index=self.actual_index_id.index_value,
            original_index=self.reference_index_id.index_value,
        )

    def _get_new_price(self):
        return (
            self.original_price
            * (self.actual_index_id.index_value / self.reference_index_id.index_value)
            if self.actual_index_id
            else False
        )

    @api.depends("original_price", "reference_index_id", "compute_date")
    def _compute_price(self):
        index_obj = self.env["l10n_be.statbel.index"]
        for record in self:
            if not record.compute_date:
                record.actual_index_id = False
                record.computed_price = False
                record.computed_formula = False
            else:
                first = record.compute_date.replace(day=1)
                lastMonth = first - datetime.timedelta(days=1)
                reference_month = lastMonth.month
                base_year = lastMonth.year
                actual_date = index_obj._format_date(reference_month, base_year)

                actual_index = index_obj.search(
                    [
                        ("index_type", "=", "health_index"),
                        ("base_year", "=", record.base_year),
                        ("display_date", "=", actual_date),
                    ]
                )
                record.actual_index_id = actual_index
                record.computed_price = record._get_new_price()
                record.computed_formula = record._get_formula_string()

    @api.depends("contract_date", "into_force_date", "region")
    def _compute_reference_month(self):
        """
        This compute the reference year and the reference month for
        the origin date.

        The origin month is always the month preceding the date when
        the contract has been signed except for the flemish region from
        the 1st of January 2019: the reference month is the one preceding
        the date when the contract came into force.
        """
        index_obj = self.env["l10n_be.statbel.index"]
        for record in self:
            origin_date = (
                record.into_force_date
                if (
                    record.region == "flemish"
                    and record.contract_date
                    and record.contract_date >= fields.Date.from_string("2019-01-01")
                )
                else record.contract_date
            )
            if origin_date:
                first = origin_date.replace(day=1)
                lastMonth = first - datetime.timedelta(days=1)
                reference_month = lastMonth.month
                base_year = lastMonth.year

                record.reference_month = index_obj._format_date(
                    reference_month, base_year
                )
            else:
                record.reference_month = False

    @api.depends("reference_month")
    def _compute_base_year(self):
        """This is the computation to find the base year to get the good
        index.
        """
        index_obj = self.env["l10n_be.statbel.index"]
        indexes = index_obj.search(
            [
                ("index_type", "=", "health_index"),
                ("display_date", "in", self.mapped("reference_month")),
            ]
        )
        self_with_month = self.filtered("reference_month")
        for record in self.filtered("reference_month"):
            year = record.reference_month.split("/")[1]
            indexes = indexes.filtered(
                lambda i: i.display_date == record.reference_month
                and i.base_year < year
            )
            index = first(indexes.sorted(key=lambda i: i.base_year, reverse=True))
            record.base_year = index.base_year
            record.reference_index_id = index
        (self - self_with_month).update({"base_year": False})
