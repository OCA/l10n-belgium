# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# Constant values that are defined by Companyweb and vary by API versions

# Companyweb is ok with those keys being visible on Github
SERVICE_INTEGRATOR_ID = "acsone"
SERVICE_INTEGRATOR_SECRET = "ECAB8ACF-9AE1-4E90-BD0D-05A1F47A3FE9"
COUNTRY_CODE_BELGIUM = "BE"
COUNTRY_CODE_NETHERLANDS = "NL"
COUNTRY_CODE_LUXEMBOURG = "LU"
ALLOWED_COUNTRY_SELECTION = [
    (COUNTRY_CODE_BELGIUM, "Belgium"),
    (COUNTRY_CODE_NETHERLANDS, "Netherlands"),
    (COUNTRY_CODE_LUXEMBOURG, "Luxembourg"),
]
ALLOWED_COUNTRY_CODES = (
    COUNTRY_CODE_BELGIUM,
    COUNTRY_CODE_NETHERLANDS,
    COUNTRY_CODE_LUXEMBOURG,
)
SYNC_PAGE_SIZE = 100  # 1-100
DATE_FORMAT = "%Y%m%d"
HASH_ENCODING = "utf-8"

# ODOO FIELDS
# Fields where the value is in the main response.
# Each comes with a corresponding <field_name>_enable field
DATA_FIELDS = [
    "cweb_name",
    "cweb_commercial_name",
    "cweb_vat_liable",
    "cweb_vat",
    "cweb_email",
    "cweb_website",
    "cweb_phone",
    "cweb_url",
    "cweb_url_report",
    "cweb_startDate",
    "cweb_endDate",
    "cweb_registry",
    "cweb_rsin_number",
    "cweb_sync",
    "cweb_main_industry",
    "cweb_peppol",
    "cweb_country_code",
]
# Fields where the value is nested within other keys
NESTED_FIELDS = {
    "cweb_jur_form": ["cweb_jur_form"],
    "cweb_companystatus": ["cweb_companystatus", "cweb_companystatus_code"],
    "cweb_prefLang_id": ["cweb_prefLang_id"],
    "cweb_address": [
        "cweb_street",
        "cweb_zip",
        "cweb_city",
        "cweb_country_code_address",
    ],
    "cweb_score": ["cweb_score", "cweb_image"],
    "cweb_creditLimit": ["cweb_creditLimit", "cweb_creditLimit_info"],
    "cweb_warnings": ["cweb_warnings"],
    "cweb_industries": ["cweb_industries"],
    "cweb_liable_party": ["cweb_liable_party"],
    "cweb_url_payment_experience": ["cweb_url_payment_experience"],
}
ADDRESS_FIELDS = [
    "cweb_address_enable",
    "cweb_street",
    "cweb_zip",
    "cweb_city",
    "cweb_country_id",
]
BALANCE_FIELDS = [
    "cweb_currency_id",
    "cweb_closed_date",
    "cweb_balance_year",
]
BALANCE_NESTED_FIELDS = [
    "cweb_equityCapital",
    "cweb_turnover",
    "cweb_average_fte",
    "cweb_addedValue",
    "cweb_result",
]
FLOAT_FIELDS = [
    "cweb_equityCapital",
    "cweb_turnover",
    "cweb_average_fte",
    "cweb_addedValue",
    "cweb_result",
    "cweb_creditLimit",
]
DATE_FIELDS = [
    "cweb_closed_date",
    "cweb_startDate",
    "cweb_endDate",
]
# Each key requires a config field 'fill_<field_name>' on company
FILL_FIELD_MAP = {
    "cweb_name": "name",
    "cweb_commercial_name": "company_name",
    "cweb_street": "street",
    "cweb_zip": "zip",
    "cweb_city": "city",
    "cweb_country_id": "country_id",
    "cweb_email": "email",
    "cweb_website": "website",
    "cweb_phone": "phone",
    "cweb_vat": "vat",
    "cweb_registry": "company_registry",
}

# COMPANYWEB API DATA KEYS
DATA_KEYS = {
    "cweb_name": "CompanyName",
    "cweb_commercial_name": "CommercialName",
    "cweb_jur_form": "LegalForm",
    "cweb_vat_liable": "VatEnabled",
    "cweb_url": "DetailUrl",
    "cweb_url_report": "ReportUrl",
    "cweb_companystatus": "CompanyStatus",
    "cweb_prefLang_id": "PreferredLanguages",
    "cweb_address": "Address",
    "cweb_balance_data": "Balances",
    "cweb_startDate": "StartDate",
    "cweb_endDate": "EndDate",
    "cweb_score": "Score",
    "cweb_creditLimit": "CreditLimit",
    "cweb_warnings": "WarningsOverview",
    "cweb_registry": "RegistrationNumber",
    "cweb_main_industry": "MainActivity",
    "cweb_industries": "Activities",
    "cweb_email": "EmailAddress",
    "cweb_website": "Website",
    "cweb_vat": "VatNumber",
    "cweb_phone": "TelephoneNumber",
    "cweb_rsin_number": "RsinNumber",
    "cweb_sync": "IsInFollowUp",
    "cweb_liable_party": "DeclarationsOfLiability",
    "cweb_peppol": "Peppol",
    "cweb_url_payment_experience": "PaymentExperience",
    "cweb_country_code": "CountryCode",
}
# Keys to access any data within DATA_KEYS above
NESTED_KEYS = {
    "cweb_jur_form": "Abbreviation",
    "cweb_companystatus": "Info",
    "cweb_companystatus_code": "Code",
    "cweb_prefLang_id": "LanguageString",
    "cweb_street": "Line1",
    "cweb_zip": "PostalCode",
    "cweb_city": "City",
    "cweb_country_code_address": "CountryCode",
    "cweb_balance_year": "FiscalYear",
    "cweb_currency_id": "Currency",
    "cweb_closed_date": "ToDate",
    "cweb_equityCapital": "UNIFIED_Equity",
    "cweb_turnover": "UNIFIED_Turnover",
    "cweb_average_fte": "UNIFIED_Employees",
    "cweb_addedValue": "UNIFIED_ProfitLoss",
    "cweb_result": "UNIFIED_GrossMargin",
    "cweb_score": "ScoreAsInt",
    "cweb_image": "ScoreImage",
    "cweb_creditLimit": "Limit",
    "cweb_creditLimit_info": "Info",
    "cweb_warnings": "Warnings",
    "cweb_warning_str": "string",
    "cweb_industries": "Activity",
    "is_main_industry": "IsMainCategory",
    "industry_name": "Description",
    "industry_code": "Code",
    "balance_data_key": "Key",
    "balance_data_value": "Value",
    "balance_data_dict_main": "Balance",
    "balance_data_dict_parent": "BalanceData",
    "balance_data_dict_child": "BalanceData",
    "cweb_liable_party": "LiableParty",
    "liable_party_name": "Name",
    "liable_party_code": "Code",
    "cweb_url_payment_experience": "ReportUrl",
}
SEARCH_RESULT_KEYS = {
    "name": "CompanyName",
    "street": "Street",
    "city": "City",
    "country": "Country",
    "country_code": "CountryCode",
    "registry": "RegistrationNumber",
    "is_active": "IsActive",
}
