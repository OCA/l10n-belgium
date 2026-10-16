# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

import requests

from odoo.fields import Command

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


def first_ean(record):
    return record[:1]


class ProductProductMapper(Component):
    _name = "product.product.medipim.mapper"
    _inherit = "importer.base.mapper"
    _apply_on = "product.product"

    direct = [  # noqa
        ("id", "medipim_id"),
        ("cnk", "cnk_code"),
        ("name", "name"),
    ]
    required = {  # noqa
        "name": "name",
    }
    translatable = ["name"]  # noqa

    defaults = [("sale_ok", True)]  # noqa

    @mapping
    def ean(self, record):
        result = {}
        ean = record.get("ean", [])
        if ean:
            result["barcode"] = ean[0]
        return result

    @mapping
    def medipimCategories(self, record):
        """
        [
            {
                "id": "string",
                "name": {
                    "nl": "string" | null,
                    "fr": "string" | null,
                    "en": "string" | null,
                    "de": "string" | null
                },
                "description": {
                    "nl": "string" | null,
                    "fr": "string" | null,
                    "en": "string" | null,
                    "de": "string" | null
                },
                "parent": "string",
                "order": 1,
                "type": "string"
            }
        ],
        """
        result = {}
        record_categories = record.get("medipimCategories", [])

        categ_ids = [record_category.get("id") for record_category in record_categories]
        if categ_ids:
            categories = self.env["product.medipim.category"].search(
                [("medipim_id", "in", categ_ids)], limit=1
            )
            if categories:
                result["medipim_category_ids"] = [Command.set(categories.ids)]
        return result

    @mapping
    def weight(self, record):
        weight_unit = record.get("weightWithUnit")
        if not weight_unit:
            return {}
        uom = self.env["uom.uom"].search(
            [("name", "=", weight_unit.get("unit"))], limit=1
        )
        result = {}
        if uom and uom.factor:
            uom_reference = self.env["uom.uom"].search(
                [
                    ("category_id", "=", uom.category_id.id),
                    ("uom_type", "=", "reference"),
                ],
                limit=1,
            )
            value = uom._compute_quantity(
                float(weight_unit.get("value")), uom_reference
            )
            result["weight"] = value
        return result

    @mapping
    def status(self, record):
        status = record.get("status")
        result = {}
        if status == "inactive":
            result["active"] = False
        return result

    def _get_image_content(self, url):
        return requests.get(url, timeout=5).content

    def _get_image_fields(self):
        return [
            ("image_1920", "hugePng"),
        ]

    @mapping
    def images(self, record):
        """
        We get the images from frontals here to have the main image for backend
        """
        photos = record.get("frontals")
        result = {}
        if photos:
            for field_name, record_field in self._get_image_fields():
                photo = sorted(photos, key=lambda p: p["displayOrder"])
                url = photo[0].get("formats").get(record_field)
                if url:
                    image_content = base64.b64encode(self._get_image_content(url))
                    result[field_name] = image_content
        return result

    @mapping
    def state(self, record):
        state = record.get("status")
        result_state = "sellable"
        if state == "replaced":
            result_state = "obsolete"
        elif state == "inactive":
            result_state = "end"
        return {"state": result_state}

    @mapping
    def product_tags(self, record):
        tags = self.env["product.tag"].search([("is_medipim", "=", True)])
        result = {}
        if tags:
            result["product_tag_ids"] = [Command.set(tags.ids)]
        return result
