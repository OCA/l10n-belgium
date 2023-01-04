from odoo import http
from odoo.http import request


class WebsiteSubscription(http.Controller):

    def get_values_from_user(self, values, is_company):
        values = super().get_values_from_user(self, values, is_company)
        if request.env.user.login != "public":
            partner = request.env.user.partner_id
            company = self.env["res.company"]._company_default_get()
            if not is_company and company.require_national_number:
                national_number_id_category = self.env.ref(
                    "l10n_be_national_number.l10n_be_national_number_category"
                    ).id
                national_number = partner.id_numbers.search(
                    [('category_id', '=', national_number_id_category)])
                values["national_number"] = national_number
        return values
