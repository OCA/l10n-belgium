# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def _get_product_description_mapping() -> dict:
    return {
        "usage": "medical_usage",
        "contra_indication": "medical_contra_indication",
        "properties": "medical_properties",
        "composition": "medical_composition",
        "full_description": "medical_full_description",
        "indication": "medical_indication",
        "nutritional_value": "medical_nutritional_value",
        "legal_text": "medical_legal_text",
    }
