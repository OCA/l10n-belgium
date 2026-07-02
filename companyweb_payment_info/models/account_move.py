# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

from odoo.addons.companyweb_base.cweb_const import ALLOWED_COUNTRY_CODES

from ..cweb_utils import cweb_send_open_invoices

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _cweb_prepare_invoice_values(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        customer_country_code = partner.country_id.code
        if customer_country_code not in ALLOWED_COUNTRY_CODES:
            return None
        if partner.company_registry:
            identifier_type = "RegistrationNumber"
            identifier = partner.company_registry
        elif partner.vat:
            identifier_type = "VatNumber"
            identifier = partner.vat
        else:
            return None
        return {
            "InvoiceNumber": self.name,
            "InvoiceDate": self.invoice_date.strftime("%Y%m%d"),
            "OpenAmountWhole": str(int(self.amount_residual)),
            "CustomerCountry": customer_country_code,
            "CustomerIdentifierType": identifier_type,
            "CustomerIdentifier": identifier,
        }

    @api.model
    def _cron_cweb_send_open_invoices(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        url = IrConfigParameter.get_param("companyweb.payex.url", "")
        if not url:
            _logger.warning(
                "Companyweb: No PayEx URL configured (companyweb.payex.url), skipping."
            )
            self.env["ir.logging"].sudo().create(
                {
                    "name": _logger.name,
                    "type": "server",
                    "level": "WARNING",
                    "message": (
                        "Companyweb: No PayEx URL configured"
                        " (companyweb.payex.url), skipping."
                    ),
                    "path": __name__,
                    "func": "_cron_cweb_send_open_invoices",
                    "line": 0,
                }
            )
            return

        module = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "companyweb_payment_info")], limit=1)
        )
        package_version = module.installed_version

        for company in self.env["res.company"].sudo().search([]):  # pylint: disable=no-search-all
            if not company.companyweb_payment_info_enable:
                continue
            if not company.cweb_login or not company.cweb_password:
                _logger.warning(
                    "Companyweb: Missing credentials for company %s, skipping.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Companyweb: Missing credentials for company"
                            f" {company.name}, skipping."
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            supplier_country_code = company.country_id.code
            if supplier_country_code not in ALLOWED_COUNTRY_CODES:
                _logger.warning(
                    "Companyweb: Unsupported supplier country %s for company %s.",
                    supplier_country_code,
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Companyweb: Unsupported supplier country"
                            f" {supplier_country_code} for company {company.name}."
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            if company.company_registry:
                supplier_identifier_type = "RegistrationNumber"
                supplier_identifier = company.company_registry
            elif company.vat:
                supplier_identifier_type = "VatNumber"
                supplier_identifier = company.vat
            else:
                _logger.warning(
                    "Companyweb: No VAT or registry number for company %s, skipping.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Companyweb: No VAT or registry number"
                            f" for company {company.name}, skipping."
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            open_invoices = self.search(
                [
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("payment_state", "in", ("not_paid", "partial")),
                    ("company_id", "=", company.id),
                ]
            )

            invoices_list = []
            for move in open_invoices:
                vals = move._cweb_prepare_invoice_values()
                if vals:
                    invoices_list.append(vals)

            if not invoices_list:
                _logger.info(
                    "Companyweb: No eligible open invoices for company %s.",
                    company.name,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Companyweb: No eligible open invoices"
                            f" for company {company.name}."
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
                continue

            company_lang = (company.partner_id.lang or "en_US")[:2].upper()
            if company_lang not in ("FR", "NL"):
                company_lang = "EN"

            status, result = cweb_send_open_invoices(
                url=url,
                login=company.cweb_login,
                password=company.cweb_password,
                lang=company_lang,
                package_version=package_version,
                supplier_country=supplier_country_code,
                supplier_identifier_type=supplier_identifier_type,
                supplier_identifier=supplier_identifier,
                invoices_list=invoices_list,
            )
            if status != 0:
                _logger.warning(
                    "Companyweb: Error %i sending open invoices for company %s: %s",
                    status,
                    company.name,
                    result,
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "WARNING",
                        "message": (
                            f"Companyweb: Error {status} sending"
                            f" open invoices for company {company.name}: {result}"
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
            else:
                summary = result or {}
                _logger.info(
                    "Companyweb: Open invoices sent for company %s — "
                    "valid: %i, invalid: %i, unique customers: %i, "
                    "total open amount: %s",
                    company.name,
                    summary.get("NumberOfValidInvoices", 0),
                    summary.get("NumberOfInvalidInvoices", 0),
                    summary.get("NumberOfUniqueCustomers", 0),
                    summary.get("TotalOpenAmountOfValidInvoices", 0),
                )
                self.env["ir.logging"].sudo().create(
                    {
                        "name": _logger.name,
                        "type": "server",
                        "level": "INFO",
                        "message": (
                            f"Companyweb: Open invoices sent for"
                            f" company {company.name} — "
                            f"valid: {summary.get('NumberOfValidInvoices', 0)}, "
                            f"invalid: {summary.get('NumberOfInvalidInvoices', 0)}, "
                            f"unique customers:"
                            f" {summary.get('NumberOfUniqueCustomers', 0)}, "
                            f"total open amount:"
                            f" {summary.get('TotalOpenAmountOfValidInvoices', 0)}"
                        ),
                        "path": __name__,
                        "func": "_cron_cweb_send_open_invoices",
                        "line": 0,
                    }
                )
