# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import re
from xml.dom import minidom

import click

# CONST
PATH = "../data/"
MIS_REPORT_MODEL = "mis.report.kpi"
# Rub_6_7 = Unallocated FY Profit (Losses)
STYLE_ID_RUB_6_7 = "mis_report_style_l10n_be_3"
STYLE_ID_AUTO_EXPAND_RUB_6_7 = "mis_report_style_l10n_be_acc_det"
ASSOCIATION_PREFIXES = ["m04", "m05", "m08"]
EXPR_RUB_10_15_ASSOCIATION = "+rub_10 +rub_12 +rub_13 +rub_14 +rub_6_7 +rub_15"

# key = rubric name, value = expression
RUBRICS_TO_CORRECT_DICT = {
    # Balance Sheet
    "bs": {
        "rub_490_1": "bals[490%,491%,499%]",
        # if the template concern an association (m-04, m-05 or m-08),
        # the expression will be EXPR_RUB_10_15_ASSOCIATION
        "rub_10_15": "+rub_10_11 +rub_12 +rub_13 +rub_14 +rub_6_7 +rub_15 -rub_19",
        "rub_174_0": "-bals[170%,171%,174%]",
        "rub_1100_10": "-bals[1100%,1110%]",
        "rub_1109_19": "-bals[1109%,1119%]",
    },
    # Profit & Loss
    "pl": {
        "rub_9900": (
            "-balp[70%,71%,72%,73%,74%,"
            "760%,761%,762%,763%,764%,765%,766%,767%,768%,60%,61%]"
        ),
        "rub_76A": "-balp[760%,761%,762%,763%,764%,765%,766%,767%,768%]",
        "rub_66A": "balp[660%,661%,662%,663%,664%,665%,666%,667%,669%]",
        "rub_76B": "-balp[769%]",
        "rub_66B": "balp[668%]",
    },
}

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.command()
@click.argument("xml-template-file", required=True, type=click.File())
# flake8: noqa: C901
def correct_xml(xml_template_file):
    """This script corrects the xml documents previously generated
    using the generate_xml script

    It corrects some expressions of specific rubrics,
    add 'Unallocated FY Profit (Losses)' in the Balance Sheet template,
    and modify the records' styles in the Profit & Loss template

    XML_TEMPLATE_FILE is the path to the xml file you want to correct
    """
    if "bs" not in xml_template_file.name and "pl" not in xml_template_file.name:
        _logger.critical("File name doesn't contain 'bs' or 'pl'")
        _logger.critical("bs" in xml_template_file.name)
        return
    rub_9900_expression = []
    for association_prefix in ASSOCIATION_PREFIXES:
        if association_prefix in xml_template_file.name:
            RUBRICS_TO_CORRECT_DICT["bs"]["rub_10_15"] = EXPR_RUB_10_15_ASSOCIATION
    with minidom.parse(PATH + xml_template_file.name) as dom:
        _remove_new_lines(dom)
        for node in dom.childNodes[1].childNodes:
            rubcode = re.search(r"rub.*", node.getAttribute("id"))
            _modify_expression(node, "pl")
            if not rubcode:
                continue
            rubcode = rubcode.group(0)
            # Balance Sheet case
            if "bs" in xml_template_file.name:
                _modify_expression(node, "bs")
                if "rub_14" in rubcode:
                    _add_unallocated_fy_profit(dom, node, xml_template_file)
                if "m87" not in xml_template_file.name:
                    continue
                # The expression of this rubric is not present in the m87
                # calculation JSON file
                if "rub_130_1" in rubcode:
                    expression = tuple(
                        filter(
                            lambda field: field.getAttribute("name") == "expression",
                            node.getElementsByTagName("field"),
                        )
                    )[0]
                    if expression.firstChild.nodeType == expression.TEXT_NODE:
                        expression.firstChild.replaceWholeText(
                            "+rub_1311 +rub_1312 +rub_1313 +rub_1319"
                        )
                # Corrects the style for rubrics 1311, 1312, 1313 and 1319
                elif "rub_131" in rubcode:
                    _modify_styles(node, 4)
            # Profit & Loss case
            else:
                if "rub_9900" == rubcode:
                    expression = tuple(
                        filter(
                            lambda field: field.getAttribute("name") == "expression",
                            node.getElementsByTagName("field"),
                        )
                    )[0].firstChild.nodeValue
                    rubcodes = re.findall(r"[+-]rub_\w*", expression)
                    for rub in rubcodes:
                        rub = re.sub(r"[+-]", "", rub)
                        rub_9900_expression.append(rub)
                elif rubcode in rub_9900_expression:
                    if rubcode == "rub_76A":
                        _modify_styles(node, 1)
                    else:
                        _modify_styles(node, 2)
                elif "rub_99" not in rubcode:
                    if rubcode == "rub_753":
                        _modify_styles(node, 3)
                    else:
                        _modify_styles(node, 1)
        # Write the result in xml_template_file
        with open(xml_template_file.name, "w") as output_xml_file:
            dom.writexml(
                output_xml_file,
                addindent="  ",
                newl="\n",
            )
        _logger.info(f"{xml_template_file.name} successfully modified.")


def _modify_expression(node, template_type):
    """Edit node to correct its expression by the new one in RUBRICS_TO_CORRECT_DICT
    :param node: The node to edit
    :param template_type: The type of the template
    """
    for rubric, expr in RUBRICS_TO_CORRECT_DICT[template_type].items():
        if rubric in node.getAttribute("id"):
            expression = tuple(
                filter(
                    lambda field: field.getAttribute("name") == "expression",
                    node.getElementsByTagName("field"),
                )
            )[0]
            if expression.firstChild.nodeType == expression.TEXT_NODE:
                expression.firstChild.replaceWholeText(expr)


def _modify_styles(node, increment):
    """Increase by 'increment' the style's id of the node,
    which correctly displays the template
    :param node: The node to edit
    """
    style_id = tuple(
        filter(
            lambda field: field.getAttribute("name") == "style_id",
            node.getElementsByTagName("field"),
        )
    )[0]
    style = re.match(r".*_(.*)", style_id.getAttribute("ref")).group(1)
    module = re.match(r"(.*_).*", style_id.getAttribute("ref")).group(1)
    if "base" not in style:
        style_id.setAttribute("ref", f"{module}{str(int(style) + increment)}")


def _add_unallocated_fy_profit(dom, node, xml_template_file):
    """Add a new record for Unallocated Fy Profit (Losses), which is not
    present in the taxonomy, and add it after node
    :param dom: The dom
    :param node: The node after which you need to insert Unallocated FY Profit
    :param xml_template_file: The file you want to edit
    """
    file_name = re.match(r".*/(.*)\..*", xml_template_file.name).group(1)
    sequence = tuple(
        filter(
            lambda field: field.getAttribute("name") == "sequence",
            node.getElementsByTagName("field"),
        )
    )[0].firstChild.nodeValue
    # Create the record
    record = dom.createElement("record")
    record.setAttribute("model", MIS_REPORT_MODEL)
    record.setAttribute("id", f"new_{file_name.replace('-', '_')}_rub_6_7")
    # Create the report_id field
    report_id = dom.createElement("field")
    report_id.setAttribute("name", "report_id")
    report_id.setAttribute("ref", f"new_{file_name.replace('-', '_')}")
    record.appendChild(report_id)
    # Create the name field
    name = dom.createElement("field")
    name.setAttribute("name", "name")
    name_text = dom.createTextNode("rub_6_7")
    name.appendChild(name_text)
    record.appendChild(name)
    # Create the description field
    description = dom.createElement("field")
    description.setAttribute("name", "description")
    description_text = dom.createTextNode("Unallocated FY Profits (Losses)")
    description.appendChild(description_text)
    record.appendChild(description)
    # Create the expression field
    expression = dom.createElement("field")
    expression.setAttribute("name", "expression")
    expression_text = dom.createTextNode("-bals[6%,7%]")
    expression.appendChild(expression_text)
    record.appendChild(expression)
    # Create the type field
    type_field = dom.createElement("field")
    type_field.setAttribute("name", "type")
    type_text = dom.createTextNode("num")
    type_field.appendChild(type_text)
    record.appendChild(type_field)
    # Create the compare_method field
    compare_method = dom.createElement("field")
    compare_method.setAttribute("name", "compare_method")
    compare_method_text = dom.createTextNode("pct")
    compare_method.appendChild(compare_method_text)
    record.appendChild(compare_method)
    # Create the style_id field
    style_id = dom.createElement("field")
    style_id.setAttribute("name", "style_id")
    style_id.setAttribute("ref", STYLE_ID_RUB_6_7)
    record.appendChild(style_id)
    # Create the sequence field
    sequence_field = dom.createElement("field")
    sequence_field.setAttribute("name", "sequence")
    sequence_text = dom.createTextNode(str(int(sequence) + 5))
    sequence_field.appendChild(sequence_text)
    record.appendChild(sequence_field)
    # Add the new node after the current node
    dom.documentElement.insertBefore(record, node.nextSibling)


def _remove_new_lines(dom):
    """Remove the '\n' in order to pretty print the xml file again"""
    for node in dom.childNodes[1].childNodes:
        if node.nodeType == dom.TEXT_NODE:
            dom.documentElement.removeChild(node)
            continue
    for node in dom.childNodes[1].childNodes:
        for child in node.childNodes:
            if child.nodeType == dom.TEXT_NODE:
                node.removeChild(child)


if __name__ == "__main__":
    correct_xml()
