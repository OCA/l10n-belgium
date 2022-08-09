# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ContractPriceRevisionWizard(models.TransientModel):

    _inherit = "contract.price.revision.wizard"

    belgium_region = fields.Selection(
        selection=[
            ("brussels", "Brussels Region"),
            ("flemish", "Flemish Region"),
            ("walloon", "Waloon Region"),
        ],
    )

    @api.model
    def _get_variation_type(self):
        res = super()._get_variation_type()
        res.append(("l10n_be_statbel", "StatBel Indexation"))
        return res

    def _get_original_price(self, line):
        self.ensure_one()
        original_line = line._get_first_ancestor()
        return original_line.price_unit

    def _get_computer_values(self, line):
        self.ensure_one()
        return {
            "contract_date": line.contract_id.date,
            "into_force_date": line.contract_id.date_start,
            "compute_date": self.date_start,
            "original_price": self._get_original_price(line),
            "region": self.belgium_region,
        }

    def _get_new_price(self, line):
        """Get the price depending the change type chosen"""
        if self.variation_type == "l10n_be_statbel":
            computer = self.env["l10n_be.statbel.indexation.computer"].create(
                self._get_computer_values(line)
            )
            if computer.computed_price:
                self._set_statbel_modifications(line, computer)
                return computer.computed_price
        return super()._get_new_price(line)

    def _set_statbel_modifications(self, line, computer):
        line.contract_id.with_context(skip_modification_mail=True).write(
            {
                "modification_ids": [
                    (
                        0,
                        0,
                        {
                            "date": self.date_start,
                            "description": _(
                                "Contract line ({}) price has been revised "
                                "from {} to {} with formula ({})"
                            ).format(
                                line.display_name,
                                line.price_unit,
                                computer.computed_price,
                                computer.computed_formula,
                            ),
                        },
                    )
                ]
            }
        )
