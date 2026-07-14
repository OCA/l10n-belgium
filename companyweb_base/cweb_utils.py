# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from hashlib import sha1

from zeep import Client
from zeep.helpers import serialize_object

from .cweb_const import (
    ALLOWED_COUNTRY_CODES,
    BALANCE_FIELDS,
    BALANCE_NESTED_FIELDS,
    DATA_FIELDS,
    DATA_KEYS,
    DATE_FORMAT,
    HASH_ENCODING,
    NESTED_FIELDS,
    NESTED_KEYS,
    SERVICE_INTEGRATOR_ID,
    SERVICE_INTEGRATOR_SECRET,
    SYNC_PAGE_SIZE,
)

# Functions to interact with Companyweb Soap Server v2.0 and parse values
# https://docs.companyweb.be/ALaCarteV2/


def get_value(data, field):
    """
    Look up key of field and check in data:
    - If enabled, return value
    Args:
        data: data dict
        field: Field name in Odoo
    Returns:
        enabled (bool),
        value if enabled else None
    """
    enable = data[DATA_KEYS[field]]["IsEnabled"]
    value = data[DATA_KEYS[field]]["Value"]
    return enable, value if enable else None


def get_enable_field(field):
    """
    Return '<field>_enable'
    Remove '_id' from field if present
    """
    return f"{field[:-3] if field[-3:] == '_id' else field}_enable"


def get_all_enable_fields():
    return [get_enable_field(field_name) for field_name in DATA_KEYS]


def get_data_values(data):
    """
    Get non-nested values from data. Return odoo field values
    For each field, add {
        <field_name>_enable: bool,
        <field_name>: value,
    }
    """
    values = {}
    for field in DATA_FIELDS:
        enable, value = get_value(data, field)
        values.update(
            {
                get_enable_field(field): enable,
                field: value,
            }
        )
    return values


def get_nested_values(data):
    """
    For each field, get NESTED_FIELDS[<parent_field>] and add
    - <parent_field>_enable: bool,
    - <nested_field>: value,
    - <nested_field>: value,
    - etc
    """
    values = {}
    for field in NESTED_FIELDS.keys():
        enable, value = get_value(data, field)
        values[get_enable_field(field)] = enable
        for nested_field in NESTED_FIELDS[field]:
            values.update(
                {
                    nested_field: value[NESTED_KEYS[nested_field]]
                    if value is not None and enable
                    else False,
                }
            )
    return values


def get_balance_values(data):
    """
    Parse balance data to Odoo values
    """
    values = {}
    balance_enable, balance_raw = get_value(data, "cweb_balance_data")
    balance_data = balance_raw and balance_raw[NESTED_KEYS["balance_data_dict_main"]][0]
    values.update(
        {
            "cweb_balance_data_enable": balance_enable,
        }
    )
    if balance_enable and balance_data:
        values.update(
            {
                balance_field: balance_data[NESTED_KEYS[balance_field]]
                for balance_field in BALANCE_FIELDS
            }
        )

        if balance_data[NESTED_KEYS["balance_data_dict_parent"]]:
            balance_details = {
                d[NESTED_KEYS["balance_data_key"]]: d[NESTED_KEYS["balance_data_value"]]
                for d in balance_data[NESTED_KEYS["balance_data_dict_parent"]][
                    NESTED_KEYS["balance_data_dict_child"]
                ]
            }
            values.update(
                {
                    balance_field: balance_details[NESTED_KEYS[balance_field]]
                    for balance_field in BALANCE_NESTED_FIELDS
                }
            )
    else:
        # Set balance fields to False if not available
        values.update(
            {
                balance_field: False
                for balance_field in (BALANCE_FIELDS + BALANCE_NESTED_FIELDS)
            }
        )

    return values


def _cweb_create_hash(login, password, secret):
    """
    Create loginhash for API
    """
    today = datetime.now().strftime(DATE_FORMAT)
    text = (today + login + password + secret).lower()
    return sha1(text.encode(HASH_ENCODING)).hexdigest()


def get_country_code_from_vat(vat):
    if vat and vat[:2] in ALLOWED_COUNTRY_CODES:
        # Get country code from vat
        return vat[:2].upper()
    return False


def _cweb_get_service_args(**kwargs):
    """
    Return matching service depending on available kwargs:
    - Search by VAT
    - Search by Company Registry
    - Search by search terms (name, city, zip)

    Args:
        **kwargs: key/value of available search terms
    Returns:
        service name
        args to call service
        any missing kwargs to choose correct service
    """
    service = False
    country_code = False
    args = {}
    missing = []
    if vat := kwargs.get("vat"):
        # Get company by vat
        service = "GetCompanyByVat"
        args["VatNumber"] = vat
        country_code = get_country_code_from_vat(vat)

    if not country_code and "country_code" in kwargs:
        country_code = kwargs.get("country_code")

    if country_code:
        args["CountryCode"] = country_code
    else:
        missing.append("Country")

    if not service:
        if registry := kwargs.get("registry"):
            # Get company by registryID and country
            service = "GetCompanyByRegistrationNumber"
            args["RegistrationNumber"] = registry
        elif search := kwargs.get("search"):
            # Search company by search term and optionally zip or city
            service = "SearchCompanies"
            args["SearchTerm"] = search
            if kwargs.get("zip"):
                args["PostalCodeOrCityName"] = kwargs.get("zip")
            elif kwargs.get("city"):
                args["PostalCodeOrCityName"] = kwargs.get("city")
        else:
            missing += ["VAT", "Company ID", "Search Term"]
    return service, args, missing


def _cweb_get(url, service, login, password, lang, args):
    """
    Call a Companyweb service and return status, result
    """
    client = Client(url)
    call = getattr(client.service, service)
    response = call(
        dict(
            Login=login,
            Password=password,
            ServiceIntegrator=SERVICE_INTEGRATOR_ID,
            LoginHash=_cweb_create_hash(login, password, SERVICE_INTEGRATOR_SECRET),
            Language=lang,
            **args,
        )
    )
    res_dict = serialize_object(response)
    if (status := res_dict["StatusCode"]) != 0:
        # Returns string
        result = res_dict["StatusMessage"]
    else:
        if service == "SearchCompanies":
            # Returns list
            result = (res_dict["SearchResponseList"] or {}).get(
                "SearchResponseItem", []
            )
        elif service == "Alerts_AddListOfCompanies":
            # Returns dict
            result = res_dict
        elif service == "Alerts_FetchBulk":
            # Returns dict
            result = res_dict
        elif service in ("GetCompanyByVat", "GetCompanyByRegistrationNumber"):
            # Returns dict
            result = res_dict["CompanyResponse"] or {}
        else:
            raise NotImplementedError

    return status, result


def cweb_get(url, login, password, lang, args):
    """
    Possible args to find company:
        - 'vat' or
        - 'registry' (Company ID) or
        - 'search' (search term) with
            - optional 'zip' (zip code)
            - optional: 'city'
        - 'country_code' (required if not present in VAT)
    """
    service, cweb_args, missing = _cweb_get_service_args(**args)
    if missing:
        return -1, missing
    return _cweb_get(url, service, login, password, lang, cweb_args)


def cweb_push(url, login, password, lang, partner_list):
    args = {
        "Companies": partner_list,
    }
    status, response = _cweb_get(
        url, "Alerts_AddListOfCompanies", login, password, lang, args
    )
    return status, response


def cweb_sync(url, login, password, lang, partner_list):
    """
    Get updates from companyweb AND/OR
    Confirm updates of partners in partner_list
    """
    args = {
        "PageSize": SYNC_PAGE_SIZE,
        "ConfirmedCompanies": {"ConfirmedCompany": partner_list},
    }
    status, response = _cweb_get(url, "Alerts_FetchBulk", login, password, lang, args)
    return status, response
