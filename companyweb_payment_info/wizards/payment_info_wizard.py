# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime
import html
import re

import zeep

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import odoo.addons.companyweb_base.models.res_partner as cweb_partner

CWEB_INVOICE_MAX_LEN = 4999
VAT_RE = re.compile(r"^(BE)?\s?0?[0-9]{4}\s?\.?[0-9]{3}\s?\.?[0-9]{3}$")


def _chunks(lst, chunk_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


class CompanyWebPaymentInfoWizard(models.TransientModel):

    _name = "companyweb_payment_info.payment_info_wizard"
    _description = "Companyweb Payment Info"
    wizard_text = fields.Html("wizard_text")
    wizard_step = fields.Char(default="step1")
    wizard_email = fields.Char("wizard_email")

    def payment_info_entry_point(self):
        if self.wizard_step == "step1":
            return self._cweb_payment_info_step1()
        elif self.wizard_step == "step2":
            return self._cweb_payment_info_step2()
        elif self.wizard_step == "step3":
            return True
        else:
            raise SystemError(_("Unexpected step %s") % self.wizard_step)

    def _check_group(self):
        if not self.env.user.has_group("companyweb_payment_info.cweb_upload"):
            raise UserError(
                _(
                    """Companyweb : You need to be in the security group :
                    Upload Companyweb Invoices to perform this action"""
                )
            )

    @api.model
    def _cweb_payment_info_step1(self):

        self._check_group()

        supplierVat = self.env.user.company_id.vat
        if not supplierVat or not supplierVat.startswith("BE"):
            raise UserError(
                _(
                    "Companyweb : You need to set a valid belgian's vat "
                    "field for the current company : %s"
                    % self.env.user.company_id.name,
                )
            )

        user_login = self.env.user.cweb_login
        user_password = self.env.user.cweb_password
        if not user_login or not user_password:
            return self._cweb_call_wizard_credentials(_("Enter your Credentials"))

        client = zeep.Client(
            "https://payex.companyweb.be/v1/PaymentExperienceService.asmx"
        )

        response_previous_period = self._get_previous_period(client, supplierVat)
        # 11/15/16 means bad credentials
        if response_previous_period["StatusCode"] in [11, 15, 16]:
            return self._cweb_call_wizard_credentials(_("Bad Credentials"))
        last_date_sent = "%02d/%d" % (
            response_previous_period["PreviousMonth"],
            response_previous_period["PreviousYear"],
        )
        period_to_send = self._get_period_to_send()
        if (
            period_to_send.month == response_previous_period["PreviousMonth"]
            and period_to_send.year == response_previous_period["PreviousYear"]
        ):
            raise UserError(
                _("Companyweb : You already submitted invoices for %s" % last_date_sent)
            )

        invoices_to_send = self._create_invoices_to_send(client)
        if len(invoices_to_send) == 0:
            raise UserError(_("Companyweb : No Invoices to send"))

        summary = self._create_step1_summary(
            response_previous_period, invoices_to_send, last_date_sent, period_to_send
        )

        wizard = self.create(
            dict(
                wizard_text=summary,
                wizard_step="step2",
                wizard_email=self.env.user.partner_id.email,
            )
        )
        return dict(wizard.get_formview_action(), target="new")

    def _get_period_to_send(self):
        today = datetime.date.today()
        first = today.replace(day=1)
        return first - datetime.timedelta(days=1)

    @api.model
    def _cweb_payment_info_step2(self):

        self._check_group()

        client = zeep.Client(
            "https://payex.companyweb.be/v1/PaymentExperienceService.asmx"
        )

        wizard_email = (
            self.wizard_email if self.wizard_email else self.env.user.partner_id.email
        )

        invoices_to_send = self._create_invoices_to_send(client)
        result_start_transaction = self._cweb_start_transaction(client, wizard_email)
        if result_start_transaction["StatusCode"] != 0:
            raise UserError(
                _(
                    "Error from Companyweb : %s : %s"
                    % (
                        result_start_transaction["StatusCode"],
                        result_start_transaction["StatusMessage"],
                    )
                )
            )
        transaction_key = result_start_transaction["TransactionKey"]
        self._cweb_send_batch(client, invoices_to_send, transaction_key)
        result_summary = self._cweb_step3_summary(
            client, transaction_key, invoices_to_send
        )

        result_commit = self._cweb_commit_tran(client, transaction_key)
        if result_commit["StatusCode"] != 0:
            raise UserError(
                _(
                    "Error from Companyweb : %s : %s"
                    % (result_commit["StatusCode"], result_commit["StatusMessage"])
                )
            )
        resume = self._create_step2_summary(result_summary.InvoicesSummary)
        wizard = self.create(dict(wizard_text=resume, wizard_step="step3"))
        return dict(wizard.get_formview_action(), target="new")

    def _cweb_commit_tran(self, client, transaction_key):
        response_tran = client.service.Step4_CommitTransaction(
            dict(
                CompanyWebLogin=self.env.user.cweb_login,
                CompanyWebPassword=self.env.user.cweb_password,
                ServiceIntegrator=cweb_partner.SERVICE_INTEGRATOR_ID,
                LoginHash=self.env["res.partner"]._cweb_create_hash(
                    self.env.user.cweb_login,
                    self.env.user.cweb_password,
                    cweb_partner.SERVICE_INTEGRATOR_SECRET,
                ),
                TransactionKey=transaction_key,
            )
        )
        return response_tran

    def _cweb_step3_summary(self, client, transaction_key, invoices_to_send):
        response_summary = client.service.Step3_GetSummary(
            dict(
                CompanyWebLogin=self.env.user.cweb_login,
                CompanyWebPassword=self.env.user.cweb_password,
                ServiceIntegrator=cweb_partner.SERVICE_INTEGRATOR_ID,
                LoginHash=self.env["res.partner"]._cweb_create_hash(
                    self.env.user.cweb_login,
                    self.env.user.cweb_password,
                    cweb_partner.SERVICE_INTEGRATOR_SECRET,
                ),
                TransactionKey=transaction_key,
            )
        )
        return response_summary

    def _create_step2_summary(self, invoice_summary):
        summary = _(
            "<h2>Companyweb upload Status</h2>"
            "Here under a small summary, the full summary "
            "will be sent to <strong>%s</strong> <br/>"
            "%s : LinesWithInvalidExpirationDate <br/>"
            "%s : LinesWithInvalidInvoiceDate <br/>"
            "%s : LinesWithInvalidInvoiceNumber <br/>"
            "%s : LinesWithInvalidOpenAmount <br/>"
            "%s : LinesWithInvalidVatNumber <br/>"
            "%s : NumberOfLinesAccepted <br/>"
            "%s : NumberOfLinesRecieved <br/>"
            % (
                self.env.user.login,
                html.escape(str(invoice_summary["LinesWithInvalidExpirationDate"])),
                html.escape(str(invoice_summary["LinesWithInvalidInvoiceDate"])),
                html.escape(str(invoice_summary["LinesWithInvalidInvoiceNumber"])),
                html.escape(str(invoice_summary["LinesWithInvalidOpenAmount"])),
                html.escape(str(invoice_summary["LinesWithInvalidVatNumber"])),
                html.escape(str(invoice_summary["NumberOfLinesAccepted"])),
                html.escape(str(invoice_summary["NumberOfLinesRecieved"])),
            )
        )
        return summary

    def _create_step1_summary(
        self,
        response_previous_period,
        invoice_to_send,
        last_period_sent,
        period_to_send,
    ):
        print_period_to_send = "%02d/%d" % (
            period_to_send.month,
            period_to_send.year,
        )
        if response_previous_period["PreviousPeriodExists"]:

            summary = _(
                "<h2>Companyweb upload</h2>"
                "You are about to submit <strong>%s</strong> open invoices <br/>"
                "to Companyweb for the company <strong>%s</strong>.<br/>"
                "The previous period that was sent is <strong>%s</strong>.<br/>"
                "Your odoo login : <strong>%s</strong> will receive a full "
                "summary at the end of this transaction <br/>"
                "Make sure you have closed your bank statements for period <strong>%s</strong>."
                % (
                    len(invoice_to_send),
                    html.escape(self.env.user.company_id.name),
                    last_period_sent,
                    self.env.user.partner_id.email,
                    print_period_to_send,
                )
            )
        else:
            summary = _(
                "<h2>Companyweb upload</h2>"
                "You are about to submit <strong>%s</strong> open invoices <br/>"
                "to Companyweb for the company <strong>%s</strong>.<br/>"
                "<strong>It's the first time you use this feature "
                "for this company</strong><br/>"
                "Your odoo login : <strong>%s</strong> will received a full summary "
                "at the end of this transaction <br/>"
                "Make sure you have closed your bank statements for "
                "period <strong>%s</strong>."
                % (
                    len(invoice_to_send),
                    html.escape(self.env.user.company_id.name),
                    self.env.user.login,
                    print_period_to_send,
                )
            )
        return summary

    def _create_invoices_to_send(self, client):
        open_invoices = self._get_open_invoices()
        if not open_invoices:
            return []

        invoice_request_type = client.get_type("ns0:InvoiceRequest")
        invoice_to_send = []

        for invoice in open_invoices:
            if not invoice.partner_id.vat:
                continue
            if not VAT_RE.match(invoice.partner_id.vat):
                continue

            to_send = invoice_request_type(
                InvoiceNumber=invoice.id,
                InvoiceDate=invoice.invoice_date.strftime("%Y%m%d"),
                ExpirationDate=invoice.invoice_date_due.strftime("%Y%m%d"),
                OpenAmount=invoice.amount_total_signed,
                VatNumber=invoice.partner_id.vat,
            )
            invoice_to_send.append(to_send)
        return invoice_to_send

    def _get_open_invoices(self):
        return self.env["account.move"].search(
            [
                ("payment_state", "=", "not_paid"),
                ("state", "=", "posted"),
                ("move_type", "in", ["out_invoice"]),
                ("company_id", "=", self.env.user.company_id.id),
            ]
        )

    def _get_previous_period(self, client, supplierVat):
        response_previous_period = client.service.GetPreviousPeriod(
            dict(
                CompanyWebLogin=self.env.user.cweb_login,
                CompanyWebPassword=self.env.user.cweb_password,
                ServiceIntegrator=cweb_partner.SERVICE_INTEGRATOR_ID,
                LoginHash=self.env["res.partner"]._cweb_create_hash(
                    self.env.user.cweb_login,
                    self.env.user.cweb_password,
                    cweb_partner.SERVICE_INTEGRATOR_SECRET,
                ),
                SupplierVat=supplierVat,
            )
        )

        if response_previous_period["StatusCode"] != 0 and response_previous_period[
            "StatusCode"
        ] not in [11, 15, 16]:
            raise UserError(
                _(
                    "Error from Companyweb : %s : %s"
                    % (
                        response_previous_period["StatusCode"],
                        response_previous_period["StatusMessage"],
                    )
                )
            )
        return response_previous_period

    def _get_module_version(self):
        version_payment = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "companyweb_payment_info")])
            .installed_version
        )
        version_base = (
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "companyweb_payment_info")])
            .installed_version
        )
        return str(version_base) + "&" + str(version_payment)

    def _cweb_send_batch(self, client, invoices_to_send, transaction_key):

        invoice_list_type = client.get_type("ns0:ArrayOfInvoiceRequest")

        for invoices_request_to_send_splitted in _chunks(
            invoices_to_send, CWEB_INVOICE_MAX_LEN
        ):
            invoice_to_send_splitted = invoice_list_type()
            invoice_to_send_splitted.InvoiceRequest = invoices_request_to_send_splitted
            client.service.Step2_SendBatch(
                dict(
                    CompanyWebLogin=self.env.user.cweb_login,
                    CompanyWebPassword=self.env.user.cweb_password,
                    ServiceIntegrator=cweb_partner.SERVICE_INTEGRATOR_ID,
                    LoginHash=self.env["res.partner"]._cweb_create_hash(
                        self.env.user.cweb_login,
                        self.env.user.cweb_password,
                        cweb_partner.SERVICE_INTEGRATOR_SECRET,
                    ),
                    TransactionKey=transaction_key,
                    InvoicesList=invoice_to_send_splitted,
                )
            )

    def _cweb_start_transaction(self, client, email):
        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)

        return client.service.Step1_StartTransaction(
            dict(
                CompanyWebLogin=self.env.user.cweb_login,
                CompanyWebPassword=self.env.user.cweb_password,
                ServiceIntegrator=cweb_partner.SERVICE_INTEGRATOR_ID,
                LoginHash=self.env["res.partner"]._cweb_create_hash(
                    self.env.user.cweb_login,
                    self.env.user.cweb_password,
                    cweb_partner.SERVICE_INTEGRATOR_SECRET,
                ),
                PackageVersion=self._get_module_version(),
                SupplierVat=self.env.user.company_id.vat,
                PeriodYear=lastMonth.year,
                PeriodMonth=lastMonth.month,
                EmailAddress=email,
            )
        )

    def _cweb_call_wizard_credentials(self, message):
        wizard_form = self.env.ref("companyweb_base.companyweb_credential_wizard")
        return {
            "name": message,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "companyweb_payment_info.credential_wizard_payment",
            "view_id": wizard_form.id,
            "target": "new",
            "context": self.env.context,
        }
