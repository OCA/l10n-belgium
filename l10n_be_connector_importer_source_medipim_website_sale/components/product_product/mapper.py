# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.fields import Command

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ProductProductMapper(Component):
    _inherit = "product.product.medipim.mapper"

    def _get_website_image_fields(self):
        return [
            ("image_1920", "huge"),
        ]

    @mapping
    def website_images(self, record):
        """
        All secondary pictures are stored in "photos"
        """
        photos = record.get("photos")
        result = {}
        if photos:
            sorted_photos = sorted(photos, key=lambda p: p["displayOrder"])
            medipim_ids = [p.get("id") for p in sorted_photos]
            existing = self.env["product.image"].browse()
            if medipim_ids:
                existing = self.env["product.image"].search(
                    [("medipim_id", "in", medipim_ids)]
                )
            product_images = []
            for photo in sorted_photos:
                if photo.get("id") in existing.mapped("medipim_id"):
                    continue
                image_fields = {
                    "name": photo.get("id"),
                    "medipim_id": int(photo.get("id")),
                }
                content = False
                for field_name, record_field in self._get_website_image_fields():
                    url = photo.get("formats").get(record_field)
                    if url:
                        image_content = base64.b64encode(self._get_image_content(url))
                        image_fields[field_name] = image_content
                        content = True
                if content:
                    product_images.append(Command.create(image_fields))
            if product_images:
                result["product_variant_image_ids"] = product_images
        return result
