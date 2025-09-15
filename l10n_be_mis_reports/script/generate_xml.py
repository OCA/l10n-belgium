# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import logging
import os
import re
from xml.dom import minidom

import click

# CONST
MIS_REPORT_MODEL = "mis.report"
MIS_REPORT_KPI_MODEL = "mis.report.kpi"
BS_REPORT_XMLID = "mis_report_bs"
PL_REPORT_XMLID = "mis_report_pl"
SPECIALSTYLES = ["9900", "9901", "9902", "9903", "9904"]
PATH = "../data/"
TEMPLATE_NAME_DICT = {
    "m01-f": "Company with capital (abridged model)",
    "m02-f": "Company with capital (full model)",
    "m04-f": "Association (abridged model)",
    "m05-f": "Association (full model)",
    "m07-f": "Company with capital (micro model)",
    "m08-f": "Association (micro model)",
    "m81-f": "Company w/o capital (abridged model)",
    "m82-f": "Company w/o capital (full model)",
    "m87-f": "Company w/o capital (micro model)",
}

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.command()
@click.option("--author", required=True, help="name of the copyright author")
@click.option("--year", required=True, help="date of the copyright")
@click.option("--filename", required=True, help="the name of the file")
@click.argument("data-file", required=True, type=click.File())
@click.argument("calc-file", required=True, type=click.File())
def generate_xml(author, year, filename, data_file, calc_file):
    """This script generates two xml documents for the balance sheet
    and the profit and loss table from DATA_FILE and CALC_FILE

    DATA_FILE is a json file where all the data of the report is stored

    CALC_FILE is a json file where accounts' calculations are stored

    The output documents will be named as mis_report_bs_FILENAME.xml
    and mis_report_pl_FILENAME.xml
    """
    if not os.path.exists(PATH):
        os.mkdir(PATH)
        _logger.info(f"{PATH} created")
    else:
        _logger.info(f"{PATH} already exists")

    # json.decoder.JSONDecodeError will be thrown if there was a problem with the files
    json_data_dict = json.load(data_file)
    json_calc_dict = json.load(calc_file)
    _generate_balance_sheet(author, year, filename, json_data_dict, json_calc_dict)
    _generate_profit_loss(author, year, filename, json_data_dict, json_calc_dict)


def _generate_balance_sheet(author, year, filename, data_dict, calc_dict):
    """
    This method generates the Balance Sheet MIS Report
    and its lines (KPI's) in a mis_report_bs.xml file.
    :param author: (string) name of the copyright author
    :param year: (string) year of the copyright
    :param data_dict: data dictionary containing data from the NBB taxonomy
    :param calc_dict: computation dictionary containing computes to
    calculate the accounts
    """

    balance_sheet = data_dict["internalModels"][0]["editorModel"]["sectionsOrTables"][2]
    xbrl_facts_list = data_dict["internalModels"][0]["factPrototypes"]
    impl = minidom.getDOMImplementation()
    xml_bs_document = impl.createDocument(None, "odoo", None)
    xml_bs_document = _write_copyright(xml_bs_document, author, year)
    template_name = (
        f" - {TEMPLATE_NAME_DICT.get(filename)}"
        if TEMPLATE_NAME_DICT.get(filename)
        else ""
    )
    bs_doc_name = (
        "BELGIUM "
        + balance_sheet["section"]["labels"]["en"]
        + f" [{filename}]{template_name}"
    )
    parsed_filename = filename.replace("-", "_")
    xml_report_id = BS_REPORT_XMLID + f"_{parsed_filename}"
    xml_bs_document = _write_report_record(xml_bs_document, bs_doc_name, xml_report_id)
    xml_bs_document = _write_report_kpi_records(
        xml_bs_document, balance_sheet, calc_dict, xml_report_id, xbrl_facts_list
    )
    with open(PATH + f"mis_report_bs_{filename}.xml", "w") as output_xml_file:
        xml_bs_document.writexml(
            output_xml_file,
            addindent="  ",
            newl="\n",
        )
    _logger.info(f"file mis_report_bs_{filename}.xml successfully created.")


def _generate_profit_loss(author, year, filename, data_dict, calc_dict):
    """
    This method generates the Profit & Loss MIS Report
    and its lines (KPI's) in a mis_report_pl.xml file.
    :param author: (string) name of the copyright author
    :param year: (string) year of the copyright
    :param data_dict: data dictionary containing data from the NBB taxonomy
    :param calc_dict: computation dictionary containing computes to
    calculate the accounts
    """
    profit_and_loss = data_dict["internalModels"][0]["editorModel"]["sectionsOrTables"][
        3
    ]
    xbrl_facts_list = data_dict["internalModels"][0]["factPrototypes"]
    impl = minidom.getDOMImplementation()
    xml_pl_document = impl.createDocument(None, "odoo", None)
    xml_pl_document = _write_copyright(xml_pl_document, author, year)
    template_name = (
        f" - {TEMPLATE_NAME_DICT.get(filename)}"
        if TEMPLATE_NAME_DICT.get(filename)
        else ""
    )
    pl_doc_name = (
        "BELGIUM "
        + profit_and_loss["section"]["labels"]["en"]
        + f" [{filename}]{template_name}"
    )
    parsed_filename = filename.replace("-", "_")
    xml_report_id = PL_REPORT_XMLID + f"_{parsed_filename}"
    xml_pl_document = _write_report_record(xml_pl_document, pl_doc_name, xml_report_id)
    xml_pl_document = _write_report_kpi_records(
        xml_pl_document, profit_and_loss, calc_dict, xml_report_id, xbrl_facts_list
    )
    with open(PATH + f"mis_report_pl_{filename}.xml", "w") as output_xml_file:
        xml_pl_document.writexml(
            output_xml_file,
            addindent="  ",
            newl="\n",
        )
    _logger.info(f"file mis_report_pl_{filename}.xml successfully created.")


def _write_copyright(xml_document, author, year):
    """
    This method writes a comment with the copyright author and date and the licence
    :param xml_document: the xml document in which we add the elements
    :param author: (string) name of the copyright author
    :param year: (string) year of the copyright
    :return: the xml document with commented copyright line
    """
    odoo = xml_document.documentElement
    copyright_text = xml_document.createComment(
        f" Copyright {year} {author}\n    License AGPL-3.0 or later"
        " (http://www.gnu.org/licenses/agpl). "
    )
    xml_document.insertBefore(copyright_text, odoo)
    return xml_document


def _write_report_record(xml_document, doc_name, report_id):
    """
    This method creates the first record of the MIS Report
    :param xml_document: the xml document in which we add the elements
    :param doc_name: (string) xml document's title
    :param report_id: (string) xml document's id
    :return: the xml document with the first report added
    """
    odoo = xml_document.documentElement
    # Create record
    first_record = xml_document.createElement("record")
    first_record.setAttribute("model", MIS_REPORT_MODEL)
    first_record.setAttribute("id", f"new_{report_id}")
    # Create field 'name' and add as record's child
    name_field = xml_document.createElement("field")
    name_field.setAttribute("name", "name")
    value = xml_document.createTextNode(doc_name)
    name_field.appendChild(value)
    first_record.appendChild(name_field)
    # Create field 'style_id' and add as record's child
    style_id_field = xml_document.createElement("field")
    style_id_field.setAttribute("name", "style_id")
    style_id_field.setAttribute("ref", "mis_report_style_l10n_be_base")
    first_record.appendChild(style_id_field)
    odoo.appendChild(first_record)
    return xml_document


def _write_report_kpi_records(
    xml_document, accounts_dict, calc_dict, report_id, xbrl_facts_list
):
    """
    This method creates all the KPI's of the MIS Report
    :param xml_document: the xml document in which we add the elements
    :param accounts_dict: dictionary containing the data regarding the accounts
    :param calc_dict: computation dictionary containing computes to
    calculate the accounts
    :param report_id: (string) xml document's id
    :param xbrl_facts_list: list containing all the XBRL facts' definitions
    with their dimensions
    :return: the xml document with all his KPI's
    """
    odoo = xml_document.documentElement
    # sequence starts at 10 and is incremented by 10 each time, following the
    # json layout
    sequence = 10
    if accounts_dict["section"]["sectionsOrTables"][0].get("section"):
        nb_tables = len(accounts_dict["section"]["sectionsOrTables"])
    else:
        nb_tables = 1
    for table_index in range(nb_tables):
        # Balance sheet case
        # if report_id == BS_REPORT_XMLID:
        if BS_REPORT_XMLID in report_id:
            data_tables = accounts_dict["section"]["sectionsOrTables"][table_index][
                "section"
            ]["sectionsOrTables"]
        # Profit & loss case
        else:
            data_tables = accounts_dict["section"]["sectionsOrTables"]
        for table_nb in range(len(data_tables)):
            data_table = data_tables[table_nb]["table"]["rows"]
            rubcode_list = _get_rubcode_list(data_table)
            for account_index in range(len(data_table)):
                nb_columns = len(data_table[account_index]["cols"])
                if (
                    data_table[account_index]["cols"][nb_columns - 2].get("fp")
                    is not None
                ):
                    rubcode = data_table[account_index]["cols"][nb_columns - 2]["fp"][
                        "rubCode"
                    ]
                    acc_name = _get_sanitized_acc_name(rubcode)
                    label_value = _get_account_label(data_table[account_index]["cols"])
                    # Create record
                    record = xml_document.createElement("record")
                    record.setAttribute("model", f"{MIS_REPORT_KPI_MODEL}")
                    record.setAttribute("id", f"new_{report_id}_{acc_name}")
                    # Create field 'report_id' and add as record's child
                    report_id_field = xml_document.createElement("field")
                    report_id_field.setAttribute("name", "report_id")
                    report_id_field.setAttribute("ref", f"new_{report_id}")
                    record.appendChild(report_id_field)
                    # Create field 'name' and add as record's child
                    name_field = xml_document.createElement("field")
                    name_field.setAttribute("name", "name")
                    value = xml_document.createTextNode(acc_name)
                    name_field.appendChild(value)
                    record.appendChild(name_field)
                    # Create field 'description' and add as record's child
                    description_field = xml_document.createElement("field")
                    description_field.setAttribute("name", "description")
                    value = xml_document.createTextNode(
                        f"{label_value.strip()} [{rubcode}]"
                    )
                    description_field.appendChild(value)
                    record.appendChild(description_field)
                    # Create field 'expression' and add as record's child
                    expression_field = xml_document.createElement("field")
                    expression_field.setAttribute("name", "expression")
                    calc = _get_operation(
                        rubcode, calc_dict, report_id, xbrl_facts_list, rubcode_list
                    )
                    value = xml_document.createTextNode(calc)
                    expression_field.appendChild(value)
                    record.appendChild(expression_field)
                    # Create field 'type' and add as record's child
                    type_field = xml_document.createElement("field")
                    type_field.setAttribute("name", "type")
                    value = xml_document.createTextNode("num")
                    type_field.appendChild(value)
                    record.appendChild(type_field)
                    # Create field 'compare_method' and add as record's child
                    compare_method_field = xml_document.createElement("field")
                    compare_method_field.setAttribute("name", "compare_method")
                    value = xml_document.createTextNode("pct")
                    compare_method_field.appendChild(value)
                    record.appendChild(compare_method_field)
                    # Create field 'style_id' and add as record's child
                    style_id_field = xml_document.createElement("field")
                    style_id_field.setAttribute("name", "style_id")
                    if rubcode in SPECIALSTYLES:
                        style_id_field.setAttribute(
                            "ref", "mis_report_style_l10n_be_2i"
                        )
                    elif rubcode == "9905":
                        style_id_field.setAttribute("ref", "mis_report_style_l10n_be_1")
                    else:
                        if report_id == PL_REPORT_XMLID:
                            style_id_field.setAttribute(
                                "ref",
                                f"mis_report_style_l10n_be_"
                                f"{_get_indent(calc_dict, rubcode, 2, rubcode_list)}",
                            )
                        else:
                            style_id_field.setAttribute(
                                "ref",
                                f"mis_report_style_l10n_be_"
                                f"{_get_indent(calc_dict, rubcode, 1, rubcode_list)}",
                            )
                    record.appendChild(style_id_field)
                    # Create field 'auto_expand_accounts' and
                    # 'auto_expand_accounts_style_id' and add as record's child
                    if _needs_auto_expand(calc) and rubcode != "9900":
                        auto_expand_field = xml_document.createElement("field")
                        auto_expand_field.setAttribute("name", "auto_expand_accounts")
                        auto_expand_field.setAttribute("eval", "True")
                        record.appendChild(auto_expand_field)

                        auto_expand_style_field = xml_document.createElement("field")
                        auto_expand_style_field.setAttribute(
                            "name", "auto_expand_accounts_style_id"
                        )
                        auto_expand_style_field.setAttribute(
                            "ref", "mis_report_style_l10n_be_acc_det"
                        )
                        record.appendChild(auto_expand_style_field)
                    # Create field 'sequence' and add as record's child
                    sequence_field = xml_document.createElement("field")
                    sequence_field.setAttribute("name", "sequence")
                    value = xml_document.createTextNode(f"{sequence}")
                    sequence += 10
                    sequence_field.appendChild(value)
                    record.appendChild(sequence_field)
                    odoo.appendChild(record)
    return xml_document


def _get_account_label(account_data_list, lang="en"):
    """
    This method gets the label of an account
    :param account_data_list: a list containing account label and data for period
                              N and N-1
    :param lang: (string) language code for the document's language
                 ('de', 'en', 'fr', 'nl')
    :return: the label of the account
    """
    label = ""
    index = 0
    # the last 3 are for the period N, N-1 and the rubcode
    while index < len(account_data_list) - 3 and len(label) == 0:
        if (account_data_list[index].get("labels")) is not None:
            label = account_data_list[index]["labels"].get(lang)
            if not label:
                break
        index += 1
    if label and len(label) == 0:
        _logger.warning("label is empty")
    return label


def _get_operation(
    account_rubcode, calc_dict, report_id, xbrl_facts_list, rubcode_list
):
    """
    This method get the operation needed to compute the account
    :param account_rubcode: (string) the account's rubric code
    :param calc_dict: computation dictionary containing computes to
    calculate the accounts
    :param report_id: (string) xml document's id
    :param xbrl_facts_list: list containing all the XBRL facts' definitions
    with their dimensions
    :param rubcode_list: list containing all the table's rubric codes
    :return: the operation needed to compute the account to string format
    """
    calc = ""
    is_asset_acc = _is_asset(account_rubcode, xbrl_facts_list)
    # if not is_asset_acc:
    #     calc += "-("
    for i in range(len(calc_dict)):
        if (
            calc_dict[i]["target"]["rubCode"] == account_rubcode
            and calc_dict[i]["period"] == "N"
        ):
            source = calc_dict[i]["sources"]
            for j in range(len(source)):
                if source[j]["operation"] == "ADD":
                    calc += "+"
                elif source[j]["operation"] == "SUB":
                    calc += "-"
                calc += _get_sanitized_acc_name(source[j]["rubCode"]) + " "
    # if not is_asset_acc:
    #     calc = calc.rstrip() + ")"
    # check if calc is empty or equals '-()'
    if len(calc) <= 3:
        # Balance sheet case
        # if report_id == BS_REPORT_XMLID:
        if BS_REPORT_XMLID in report_id:
            if is_asset_acc:
                calc = f"bals[{_split_rubcode(account_rubcode, rubcode_list)}]"
            # Revert value if equity account
            else:
                calc = f"-bals[{_split_rubcode(account_rubcode, rubcode_list)}]"
        # Profit & loss case
        else:
            if is_asset_acc:
                calc = f"balp[{_split_rubcode(account_rubcode, rubcode_list)}]"
            # Revert value if equity account
            else:
                calc = f"-balp[{_split_rubcode(account_rubcode, rubcode_list)}]"
    return calc.strip()


def _is_asset(account_rubcode, xbrl_facts_list):
    """
    This method verifies if account_rubcode is an asset account,
    expressed by 'part:m1' dimension in the json data file
    :param account_rubcode: (string) the account's rubric code
    :param xbrl_facts_list: list containing all the XBRL facts' definitions
    with their dimensions
    :return: True if account_rubcode is an asset account
    """
    for index in range(len(xbrl_facts_list)):
        if xbrl_facts_list[index].get("rubCode") is not None:
            if (
                xbrl_facts_list[index]["period"] == "N"
                and xbrl_facts_list[index]["rubCode"] == account_rubcode
            ):
                for dim_index in range(len(xbrl_facts_list[index]["dims"])):
                    if (
                        xbrl_facts_list[index]["dims"][dim_index]["dimQname"]
                        == "dim:part"
                    ):
                        member_q_name = xbrl_facts_list[index]["dims"][dim_index][
                            "memberQname"
                        ]
                        return (
                            member_q_name == "part:m1"
                            or member_q_name == "part:m4"
                            and not account_rubcode.startswith("7")
                        )
                return False


def _get_indent(calc_dict, account_rubcode, indent, rubcode_list):
    """
    This method gets the position of an account in the tree,
    based of the number of parents he gets
    :param calc_dict: computation dictionary containing computes to
    calculate the accounts
    :param account_rubcode: (string) the account's rubric code
    :param indent: (int) the position in the tree
    :param rubcode_list: list containing all the table's rubric codes
    :return: the position of account_rubcode in the tree
    """
    new_rubcode = account_rubcode
    found = False
    i = 0
    while i < len(calc_dict) and not found:
        for j in range(len(calc_dict[i]["sources"])):
            if calc_dict[i]["sources"][j]["rubCode"] == account_rubcode:
                new_rubcode = calc_dict[i]["target"]["rubCode"]
                found = True
        i += 1
    # Don't increment indent if account starts with 99xx or if the rubcode is
    # not displayed in the list
    if found:
        if re.search(r"^99", new_rubcode) is not None:
            indent = _get_indent(calc_dict, new_rubcode, indent, rubcode_list)
        elif account_rubcode not in rubcode_list:
            indent = _get_indent(calc_dict, new_rubcode, indent, rubcode_list)
        else:
            indent = _get_indent(calc_dict, new_rubcode, indent + 1, rubcode_list)
    return indent


def _needs_auto_expand(calc_expr):
    """
    This method verifies if the compute expression contains 'bal'
    :param calc_expr: (string) the calculation expression needed to calculate an account
    :return: True if the calculation expression contains 'bal'
    """
    return "bal" in calc_expr


def _get_sanitized_acc_name(account_rubcode):
    """
    This method sanitize the name of the account replacing '/' by '_'
    :param account_rubcode: (string) the account's rubric code
    :return: the account's name sanitized
    """
    return f"rub_{account_rubcode.replace('/', '_')}"


def _split_rubcode(account_rubcode, rubcode_list):
    """
    This method split a rubric code. For example, the rubcode '640/8'
    will be returned as '640%, 641%, 642%, 643%, 644%, 645%, 646%, 647%, 648%'
    :param account_rubcode: (string) the account's rubric code
    :param rubcode_list: list containing all the table's rubric codes
    :return: the rubric code split
    """
    if "/" in account_rubcode:
        first_account, last_account = account_rubcode.split("/")
        # add first figures to the last accounts if the account has >= 3 figures
        if len(first_account) >= 3:
            last_account_length = len(last_account)
            last_account = first_account[:-last_account_length] + last_account
    else:
        first_account = account_rubcode
        last_account = account_rubcode

    if re.search(r"[a-zA-Z]", account_rubcode) is None:
        result = _create_rubcode_sequence(
            first_account, "", last_account, "", rubcode_list
        )
    # Case if there is a letter in the account
    else:
        first_account_letter = first_account[-1]
        first_account = first_account[:-1]
        last_account_letter = last_account[-1]
        last_account = last_account[:-1]
        result = _create_rubcode_sequence(
            first_account,
            first_account_letter,
            last_account,
            last_account_letter,
            rubcode_list,
        )
    return result


def _create_rubcode_sequence(
    first_account, first_account_letter, last_account, last_account_letter, rubcode_list
):
    """
    This method enumerates a sequence of rubric codes from first_account to last_account
    adding '%' after each rubric code
    :param first_account: (string) the account rubric  from which we start to enumerate
    :param first_account_letter: (string) the first account's letter (can be empty)
    :param last_account: (string) the account rubric from which we stop to enumerate
    :param last_account_letter: (string) the last account's letter (can be empty)
    :param rubcode_list: list containing all the table's rubric codes
    :return: a sequence of rubric codes
    """
    result = ""
    nb_of_accounts = len(range(int(first_account), int(last_account) + 1))
    if first_account[0] < last_account[0]:
        result = (
            f"{first_account}{first_account_letter}%,"
            f"{last_account}{last_account_letter}%"
        )
    else:
        for account_nb in range(int(first_account), int(last_account) + 1):
            if str(account_nb) not in rubcode_list:
                # if last account, no ','
                if int(last_account) == int(account_nb):
                    result += f"{account_nb}{last_account_letter}%"
                else:
                    result += f"{account_nb}{first_account_letter}%,"
            # Case if the account is in the list
            elif nb_of_accounts == 1:
                result += f"{account_nb}{last_account_letter}%"
    return result


def _get_rubcode_list(account_data_list):
    """
    This method gets the list of all the rubric codes in accounts_list
    :param account_data_list: a list containing account label and data for period
                              N and N-1
    :return: a list containing all account_data_list's rubric codes
    """
    rubcodes = []
    for i in range(len(account_data_list)):
        nb_columns = len(account_data_list[i]["cols"])
        # verify if [nb_columns - 2] is not out of range
        if account_data_list[i]["cols"][nb_columns - 2].get("fp") is not None:
            rubcodes.append(
                account_data_list[i]["cols"][nb_columns - 2]["fp"]["rubCode"]
            )
    return rubcodes


if __name__ == "__main__":
    generate_xml()
