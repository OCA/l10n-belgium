# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from zeep import Client
from zeep.helpers import serialize_object

from odoo.addons.companyweb_base.cweb_const import (
    SERVICE_INTEGRATOR_ID,
    SERVICE_INTEGRATOR_SECRET,
)
from odoo.addons.companyweb_base.cweb_utils import _cweb_create_hash


def cweb_send_open_invoices(
    url,
    login,
    password,
    lang,
    package_version,
    supplier_country,
    supplier_identifier_type,
    supplier_identifier,
    invoices_list,
):
    """
    Send open invoices to Companyweb AutoPayex API (v4.0).
    Returns the serialized response dict.
    """
    client = Client(url)
    response = client.service.SendOpenInvoices(
        request=dict(
            Login=login,
            Password=password,
            ServiceIntegrator=SERVICE_INTEGRATOR_ID,
            LoginHash=_cweb_create_hash(login, password, SERVICE_INTEGRATOR_SECRET),
            Language=lang,
            PackageVersion=package_version,
            SupplierCountry=supplier_country,
            SupplierIdentifierType=supplier_identifier_type,
            SupplierIdentifier=supplier_identifier,
            InvoicesList={"InvoiceRequest": invoices_list},
        )
    )
    res_dict = serialize_object(response)
    status = res_dict.get("StatusCode", -1)
    if status != 0:
        return status, res_dict.get("StatusMessage", "")
    return status, res_dict.get("InvoicesSummary", {})
