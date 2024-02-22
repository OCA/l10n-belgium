# Copyright 2023 ACSONE SA/V
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def load_taxes(env):
    # Inspirated from :
    # https://github.com/odoo/odoo/blob/0d67107ab2fc048d8b9fdf11296db1460ba539ac
    # /addons/l10n_in_tcs_tds/__init__.py#L13
    in_chart_template = env.ref("l10n_be.l10nbe_chart_template")
    for company in env["res.company"].search(
        [("chart_template_id", "=", in_chart_template.id)]
    ):
        try:
            with env.cr.savepoint():
                tax_template_ids = (
                    env["ir.model.data"]
                    .search(
                        [
                            ("module", "=", "l10n_be_antibiotic_tax"),
                            ("model", "=", "account.tax.template"),
                        ]
                    )
                    .mapped("res_id")
                )
                generated_tax_res = (
                    env["account.tax.template"]
                    .browse(tax_template_ids)
                    ._generate_tax(company)
                )
                taxes_ref = generated_tax_res["tax_template_to_tax"]
        except Exception:
            taxes_ref = {}
            _logger.error(
                "Can't load Antibiotic taxes for company: %s(%s).",
                company.name,
                company.id,
            )
        if taxes_ref:
            try:
                with env.cr.savepoint():
                    account_ref = {}
                    # Generating Accounts from templates.
                    account_template_ref = in_chart_template.generate_account(
                        taxes_ref, {}, in_chart_template.code_digits, company
                    )
                    account_ref.update(account_template_ref)

                    # writing account values after creation of accounts
                    for key, value in generated_tax_res["account_dict"][
                        "account.tax.repartition.line"
                    ].items():
                        if value["account_id"]:
                            key.write(
                                {
                                    "account_id": account_ref.get(value["account_id"]),
                                }
                            )
            except Exception:
                _logger.error(
                    "Can't load Antibiotic account so account is not set"
                    " in taxes of company: %s(%s).",
                    company.name,
                    company.id,
                )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    load_taxes(env)
