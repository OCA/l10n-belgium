from odoo import http
from odoo.http import request


class WebsiteSubscription(http.Controller):

    def get_values_from_user(self, values, is_company):
        sub_req_obj = request.env["subscription.request"]
        values = super().get_values_from_user(self, values, is_company)
        if request.env.user.login != "public":
            partner = request.env.user.partner_id
            if not is_company and sub_req_obj._check_national_number_required(self):  # noqa
                values["national_number"] = sub_req_obj.get_national_number_from_partner(partner)  # noqa
        return values
