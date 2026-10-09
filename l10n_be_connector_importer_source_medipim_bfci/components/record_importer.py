# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class MedipimRecordImporter(Component):
    _name = "medipim.importer.record"
    _inherit = "importer.record"
    _record_handler_usage = "medipim.record"

    def required_keys(self, create=False):
        res = super().required_keys()
        new_res = {}
        for source_key, dest_key in res.items():
            if source_key == "medipim_id":
                new_res["id"] = ("medipim_id",)
            else:
                new_res[source_key] = dest_key
        return new_res

    def _get_translations(self, result_line):
        """
        For each field declared in translatable, extract the simple
        keys (en, fr, nl)
        """
        for key in self.translatable_keys():
            for lang in self.translatable_langs():
                regional = self.work.options.importer.get(
                    "translation_use_regional_lang", False
                )
                if not regional:
                    lang = lang[:2]
                line_value = result_line.get(key)
                tkey = self.make_translation_key(key, lang)
                if line_value:
                    current_value_lang = line_value.get(lang)
                    result_line[tkey] = (
                        current_value_lang
                        if current_value_lang
                        else line_value.get("fr")
                    )
                else:
                    result_line[tkey] = result_line.get(key).get("fr")
            result_line[key] = result_line.get(key).get("fr")
        return result_line

    def _get_log_total_message(self, meta):
        message = self.env._(
            "Number of total products queried: %(total)s (Index: %(index)s)",
            total=meta.get("total", "N/A"),
            index=meta.get("index", "N/A"),
        )
        return message

    def _record_lines(self) -> list:
        """
        Medipim response is like:
        {
            "meta": {
                "total": <total>,
                "index": <index>,
            },
            "result": [{<result>}]
        }

        So, remove the meta key to keep only the result one
        """
        results = super()._record_lines()
        result_data = []
        for result in results:
            meta = result.get("meta")
            self.tracker._log(self._get_log_total_message(meta))
            result_line = result.get("result")
            if isinstance(result_line, list):
                result_data.extend(result_line)
            else:
                result_data.append(result_line)
        return result_data

    def _cleanup_line(self, line):
        result = super()._cleanup_line(line)
        result["_line_nr"] = 1
        return self._get_translations(result)
