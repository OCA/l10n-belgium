from odoo import fields, models, _
from odoo.exceptions import UserError


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    national_number = fields.Char(string="National Number")

    def get_required_field(self):
        required_fields = super().get_required_field()
        company = self.env["res.company"]._company_default_get()
        if company.require_national_number:
            required_fields.append("national_number")
        return required_fields

    def create_coop_partner(self):
        company = self.env["res.company"]._company_default_get()
        if company.require_national_number and not self.national_number:
            raise UserError(_("The National Number is required."))
        partner = super().create_coop_partner()
        if company.require_national_number:
            if not self.is_company:
                values = {
                    "name": self.national_number,
                    "category_id": self.env.ref(
                        "l10n_be_national_number.l10n_be_national_number_category"
                        ).id,
                    "partner_id": partner.id,
                }
                self.env["res.partner.id_number"].create(values)
        return partner

    def get_representative_vals(self):
        contact_vals = super().get_representative_vals()
        contact_vals["national_number"] = self.national_number
        return contact_vals

    def get_partner_vals(self):
        contact_vals = super().get_partner_vals()
        contact_vals["national_number"] = self.national_number
        return contact_vals

    def get_person_info(self, partner):
        super().get_person_info(partner)
        self.national_number = partner.national_number
