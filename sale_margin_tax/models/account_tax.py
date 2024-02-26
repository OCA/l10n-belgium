# Copyright 2020 ACSONE SA/NV
# Copyright 2023 len-foss/Financial Way
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class AccountTax(models.Model):
    """Add the margin amount type.
    Such a tax is kind of a meta-tax: it has to be applied on the margin,
    defined as (selling price - buying price).
    However it is not possible to compute this value from the standard arguments to
    tax compute method (compute_amount, compute_all).

    Since a margin tax is necessarily price-included, this means the selling price
    is correct, but the tax amount is simply missing.
    Therefore it adds a method that allows to replace a margin tax by a standard tax.

    The margin tax should either be computed from the lot/serial number,
    up from a purchase order. This module simply assumes the standard price can be used,
    and leave to overrides the possibility compute the margin from stock information.

    https://finances.belgium.be/fr/entreprises/
        tva/assujettissement_a_la_tva/regime_imposition_de_la_marge
    """

    # *
    # v13: see 0356933bee991a56279864421ae62e07defd025b taxes cannot be inactive anymore
    # override the default view to add the filter that tax group is not the margin one.
    # inactive taxes came back before 16.0

    _inherit = "account.tax"

    amount_type = fields.Selection(
        selection_add=[("margin", "Tax on margin")], ondelete={"margin": "cascade"}
    )
    margin_name_template = fields.Char(
        translate=True,
        string="Template used for the generated tax names",
        default="Margin: {}%",
        help="This name must accept the rate as parameter, e.g. use 'Margin: {}%'",
    )
    margin_description_template = fields.Char(
        translate=True,
        string="Template used for the generated tax description",
        default="Margin: {:.2f}%",
        help="This name can accept the rate as parameter, e.g. use 'Margin: {:.2f}%'",
    )

    def _get_or_create_margin_tax(self, base_amount, margin):
        """On non margin tax, simply return the tax;
        if the margin is not positive, return no tax;
        otherwise, determine the tax rate for the particular line,
        and try to find a matching tax, or create it on the fly.
        """
        self.ensure_one()
        if self.amount_type != "margin":
            return self
        if margin <= 0:  # we sell for less than we bought, so no tax to apply
            return self.browse()
        # La base d'imposition est constituée par la marge bénéficiaire réalisée
        # par l'assujetti-revendeur, diminuée du montant de la TVA afférente
        # à la marge bénéficiaire elle-même.
        tax_on_margin = margin - margin / (1 + self.amount / 100)
        tax_percent = (base_amount / (base_amount - tax_on_margin) - 1) * 100
        vals = {"amount": tax_percent, "type_tax_use": "sale", "amount_type": "percent"}
        vals["company_id"] = self.company_id.id
        vals["include_base_amount"] = self.include_base_amount
        vals["price_include"] = self.price_include
        vals["tax_group_id"] = self.tax_group_id.id
        domain = [(k, "=", v) for k, v in vals.items()]
        Tax = self.env["account.tax"].with_context(active_test=False).sudo()
        tax = Tax.search(domain, limit=1)
        if not tax:
            vals["active"] = False  # see *
            vals["name"] = self._get_margin_tax_name(tax_percent)
            desc_template = self.margin_description_template or ""
            vals["description"] = desc_template.format(tax_percent)
            tax = Tax.create(vals)
        return tax

    def _get_margin_tax_name(self, tax_percent):
        name_template = self.margin_name_template or "{}%"
        decimals = 1
        exists = True
        while exists:
            decimals += 1
            formatted_rate = f"{tax_percent:.{decimals}f}"
            name = name_template.format(formatted_rate)
            domain_name = [("name", "=", name), ("type_tax_use", "=", "sale")]
            exists = self.with_context(active_test=False).search(domain_name)
        return name

    def _compute_amount(
        self,
        base_amount,
        price_unit,
        quantity=1.0,
        product=None,
        partner=None,
        fixed_multiplicator=1,
    ):
        """This is a dummy method to comply with the tax interface.
        A margin tax is a placeholder for a real tax computed at invoicing time.
        """
        if self.amount_type == "margin":
            return 0  # dummy value
        return super()._compute_amount(
            base_amount, price_unit, quantity, product, partner, fixed_multiplicator
        )

    @api.constrains("amount_type")
    def _check_margin_taxes(self):
        for tax in self:
            if tax.amount_type == "margin":
                tax.price_include = True
                tax.include_base_amount = True

    def _apply_margin_taxes(self, price, purchase_price):
        margin = price - purchase_price
        taxes = self.browse()
        for tax in self:
            taxes |= tax._get_or_create_margin_tax(price, margin)
        return taxes

    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        """Override to remove the margin tax from the tax lines,
        and add it to the untaxed amount.
        """
        res = super()._prepare_tax_totals(base_lines, currency, tax_lines=tax_lines)
        filtered_groups = []
        hidden_taxes = 0
        margin_group = self.env.ref("sale_margin_tax.tax_group_margin")
        keys = list(res["groups_by_subtotal"].keys())
        if len(keys) == 1:
            group_key = keys[0]
        else:  # make sure we get the right one
            # if someone changes the translation of Untaxed Amount inconsistently
            # with the value in the account module, that would break
            group_key = margin_group.preceding_subtotal or _("Untaxed Amount")
        groups = res["groups_by_subtotal"].get(group_key, [])
        for group in groups:
            if group["tax_group_id"] != margin_group.id:
                filtered_groups.append(group)
            else:
                hidden_taxes += group["tax_group_amount"]
        if hidden_taxes:
            new_untaxed = res["amount_untaxed"] + hidden_taxes
            new_formatted = formatLang(self.env, new_untaxed, currency_obj=currency)
            res["amount_untaxed"] = new_untaxed
            res["formatted_amount_untaxed"] = new_formatted
            res["groups_by_subtotal"]["Untaxed Amount"] = filtered_groups
            if not filtered_groups:
                res["subtotals"] = []
                res["groups_by_subtotal"].pop("Untaxed Amount")
                res["subtotals_order"] = []
            else:
                res["subtotals"][0]["amount"] = new_untaxed
                res["subtotals"][0]["formatted_amount"] = new_formatted
        return res
