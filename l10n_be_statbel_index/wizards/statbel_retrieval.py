# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import tempfile

import requests
from openpyxl import load_workbook

from odoo import _, fields, models
from odoo.exceptions import UserError


class StatBelRetrieval(models.TransientModel):

    _name = "l10n_be.statbel.retrieval"
    _description = "Wizard to retrieve Statbel indexes"

    url = fields.Char(
        default="https://statbel.fgov.be/sites/default/files/files/opendata/"
        "Consumptieprijsindex%20en%20gezondheidsindex/CPI%20All%20base%20years.xlsx"
    )

    def _get_data(self, res_request):
        """Return a list of dict per index type
        [
            "date (e.g.: 1/2019)": {
                "base_year (e.g.: 2013)" : {
                    "consumer_index": value,
                    "consumer_index_wo_ene": value,
                    "consumer_index_wo_ptrl": value,
                    "inflation": value,
                    "health_index": value,
                    "smooth_health_index": value,
                }
            }
        ]
        """
        tempdir = tempfile.mkdtemp(prefix="odoo")
        filename = tempdir + "CPI All base years.xlsx"
        with open(filename, "wb") as xlsx:
            xlsx.write(res_request.content)
        wb = load_workbook(filename, read_only=True)
        values_by_date_and_ref = dict()
        sheet = wb.worksheets[0]
        rows = sheet.rows
        next(rows)
        for row in rows:
            if row[0].value is None:
                continue
            format_date = self._format_date(row[1].value, row[0].value)
            date_ref = str(int(row[9].value))
            if format_date in values_by_date_and_ref:
                if date_ref not in values_by_date_and_ref[format_date]:
                    values_by_date_and_ref[format_date][date_ref] = {}
            else:
                values_by_date_and_ref[format_date] = {date_ref: {}}
            values_by_date_and_ref[format_date][date_ref].update(
                {
                    "consumer_index": row[2].value,
                    "consumer_index_wo_ene": row[3].value,
                    "consumer_index_wo_ptrl": row[4].value,
                    "inflation": row[6].value,
                    "health_index": row[7].value,
                    "smooth_health_index": row[8].value,
                }
            )
        return values_by_date_and_ref

    def _get_index_domain(self):
        return []

    def _prepare_index(self, date, base_year, row):
        date_str = self._extract_date(date)
        month = int(date_str[0])
        year = int(date_str[1])
        values = []
        for i_type, value in row.items():
            values.append(
                {
                    "month": month,
                    "year": year,
                    "base_year": base_year,
                    "index_value": value,
                    "index_type": i_type,
                }
            )
        return values

    def _integrate_data(self, data):
        index_obj = self.env["l10n_be.statbel.index"]
        values_to_create = []
        indexes = index_obj.search(self._get_index_domain())
        indexes_by_date_and_ref = dict()
        for index in indexes:
            if index.display_date in indexes_by_date_and_ref:
                if index.base_year not in indexes_by_date_and_ref[index.display_date]:
                    indexes_by_date_and_ref[index.display_date].append(index.base_year)
            else:
                indexes_by_date_and_ref[index.display_date] = [index.base_year]

        for data_date, data_ref_year in data.items():
            if data_date not in indexes_by_date_and_ref:
                # The date is not present in existing indexes, so creating
                # each value per base year
                for year in data_ref_year:
                    values_to_create.extend(
                        self._prepare_index(data_date, year, data_ref_year[year])
                    )
            else:
                for year in data_ref_year:
                    if year not in indexes_by_date_and_ref[data_date]:
                        values_to_create.extend(
                            self._prepare_index(data_date, year, data_ref_year[year])
                        )

        if values_to_create:
            index_obj.create(values_to_create)

    def _format_date(self, month, year):
        return "{month}/{year}".format(month=int(month), year=int(year))

    def _extract_date(self, date):
        return date.split("/")

    def retrieve_statbel(self):
        res_request = requests.get(self.url)
        if res_request.status_code != requests.codes.ok:
            raise UserError(
                _("Got an error %d when trying to download the file %s.")
                % (res_request.status_code, self.url)
            )
        data = self._get_data(res_request)
        self._integrate_data(data)
