# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import io
import logging
import os

import odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CN_file_year = "2022"
CN_file_delimiter = ";"
CN_LANGS = {
    "en": _("English"),
    "nl": _("Dutch"),
    "fr": _("French"),
    "de": _("German"),
}


class IntrastatInstaller(models.TransientModel):
    _name = "intrastat.installer"
    _inherit = "res.config.installer"
    _description = "Intrastat Installer"

    CN_file = fields.Selection(
        selection="_selection_CN_file",
        string="Intrastat Code File",
        required=True,
        default=lambda self: self._default_CN_file(),
    )
    share_codes = fields.Boolean(
        string="Share Codes",
        default=True,
        help="Set this flag to share the Intrastat Codes between all "
        "Legal Entities defined in this Odoo Database.\n"
        "This may cause conflicts when requiring Intrastat declarations "
        " in multiple countries.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        required=True,
        string="Company",
    )

    @api.model
    def _selection_CN_file(self):
        return [
            (CN_file_year + "_" + x, CN_file_year + " " + CN_LANGS[x]) for x in CN_LANGS
        ]

    @api.model
    def _default_CN_file(self):
        lang = self.env.user.lang[:2]
        if lang not in ["fr", "nl"]:
            lang = "en"
        return CN_file_year + "_" + lang

    @api.model
    def _default_company_id(self):
        return self.env.company

    def _set_intrastat_fpos(self, company):
        module = (
            self.env["ir.module.module"]
            .sudo()
            .search(
                [
                    ("name", "in", ("l10n_be", "l10n_be_coa_multilang")),
                    ("state", "=", "installed"),
                ]
            )
        )
        if not module:
            _logger.warning(
                "No Belgian localisation module found. "
                "The Intrastat flag on the Intracommunity Fiscal Position "
                "has not been set."
            )
            return
        if module.name == "l10n_be":
            fpt_name = "fiscal_position_template_3"
        elif module.name == "l10n_be_coa_multilang":
            fpt_name = "afptn_intracom"
        fpos_ref = "{}.{}_{}".format(module.name, company.id, fpt_name)
        if fpos_ref:
            try:
                fpos = self.env.ref(fpos_ref)
                if not fpos.intrastat:
                    fpos.intrastat = True
            except Exception:
                _logger.warning("Fiscal position '%s' not found", fpos_ref)

    @api.model
    def _load_code(self, row, be_cn_codes, cn_codes, cn_lookup):
        company_id = self.company_id.id
        if self.share_codes:
            company_id = False
        vals = {
            "description": row["description"],
            "company_id": company_id,
        }
        cn_unit_id = row["unit_id"]
        if cn_unit_id:
            cn_unit_ref = "intrastat_product." + cn_unit_id
            cn_unit = self.env.ref(cn_unit_ref)
            vals["intrastat_unit_id"] = cn_unit.id
        cn_code = row["code"]
        cn_code_i = cn_lookup.get(cn_code)
        if isinstance(cn_code_i, int):
            be_cn_codes[cn_code_i].write(vals)
        else:
            vals["local_code"] = cn_code
            self.env["hs.code"].create(vals)

    def execute(self):
        res = super().execute()
        company = self.company_id

        # set company defaults
        module = __name__.split("addons.")[1].split(".")[0]
        transaction = self.env.ref("%s.intrastat_transaction_11" % module)
        if not company.intrastat_transaction_out_invoice:
            company.intrastat_transaction_out_invoice = transaction
        if not company.intrastat_transaction_out_refund:
            company.intrastat_transaction_out_refund = transaction
        if not company.intrastat_transaction_in_invoice:
            company.intrastat_transaction_in_invoice = transaction
        if not company.intrastat_transaction_in_refund:
            company.intrastat_transaction_in_refund = transaction

        # set intrastat flag on Intracommunity Fiscal Position
        self._set_intrastat_fpos(company)

        # Set correct company_id on intrastat transactions.
        # Installation of this module under OdooBot will
        # set the company_id to 1 in stead of company that
        # needs the Belgian Intrastat Declaration.
        # TODO: make OCA PR for intrastat_product to make
        # shared intrastat transactions the default behaviour
        self.env.cr.execute(
            """
        SELECT imd.res_id FROM ir_model_data imd
        JOIN intrastat_transaction it ON imd.res_id=it.id
        WHERE imd.module=%s AND imd.model='intrastat.transaction'
          AND it.company_id IS NOT NULL
          AND it.company_id != %s
            """,
            (module, self.company_id.id),
        )
        trans_ids = [x[0] for x in self.env.cr.fetchall()]
        if trans_ids:
            self.env.cr.execute(
                """
            UPDATE intrastat_transaction
            SET company_id = %s
            WHERE id IN %s
                """,
                (self.company_id.id, tuple(trans_ids)),
            )

        # load intrastat_codes
        hs_codes = self.env["hs.code"].search(
            ["|", ("company_id", "=", company.id), ("company_id", "=", False)]
        )
        cn_lookup = {}
        for i, c in enumerate(hs_codes):
            cn_lookup[c.local_code] = i
        for adp in odoo.addons.__path__:
            module_path = adp + os.sep + module
            if os.path.isdir(module_path):
                break
        CN_fn = self.CN_file + "_intrastat_codes.csv"
        CN_fqn = module_path + os.sep + "static/data" + os.sep + CN_fn
        iso_code = self.CN_file[-2:]
        langs = self.env["res.lang"].search([("code", "=like", iso_code + "_%")])

        if not langs:
            raise UserError(
                _("Language %s is not activated on your system") % CN_LANGS[iso_code]
            )
        with io.open(CN_fqn, mode="r", encoding="Windows-1252") as CN_file:
            cn_codes = csv.DictReader(CN_file, delimiter=CN_file_delimiter)
            for lang in langs:
                ctx = dict(self.env.context, lang=lang.code)
                hs_codes = hs_codes.with_context(ctx)
                for row in cn_codes:
                    self._load_code(row, hs_codes, cn_codes, cn_lookup)
        return res
