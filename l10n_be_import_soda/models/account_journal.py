# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import io

from lxml import etree

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_soda = fields.Boolean(string="Import SODA", default=False)

    def create_document_from_attachment(self, attachment_ids=None):
        journal = self or self.browse(self.env.context.get("default_journal_id"))
        soda_files, non_soda_files = [], []
        if attachment_ids and journal.import_soda:
            attachments = self.env["ir.attachment"].browse(attachment_ids or [])
            soda_files = attachments.filtered(journal._is_soda_file)
            non_soda_files = attachments - soda_files
        if soda_files:
            moves = journal._import_soda_file(soda_files)
            other_moves = self.env["account.move"]
            if non_soda_files:  # process other files as usual
                other_moves = self._create_document_from_attachment(non_soda_files)
            if other_moves:
                moves += other_moves
            result = self._get_move_action(moves)
        else:  # this will directly return a window action
            result = super().create_document_from_attachment(attachment_ids)
        return result

    def _is_soda_file(self, attachment):
        try:
            xml_content = self._parse_soda_from_attachment(attachment)
            root_tag = xml_content.getroot().tag
            is_soda_file = root_tag == "SocialDocument"
        except etree.XMLSyntaxError:
            is_soda_file = False
        return is_soda_file

    def _parse_soda_from_attachment(self, attachment):
        # unsafe method, make sure to call it with a valid attachment
        # or in a try/except block
        return etree.parse(io.BytesIO(attachment.raw))  # noqa: S320

    def _import_soda_files(self, attachments):
        moves = self.env["account.move"]
        for attachment in attachments:
            moves += self._import_soda_file(attachment)
        return moves

    def _import_soda_file(self, attachment, move=None):
        self.ensure_one()

        soda_xml = self._parse_soda_from_attachment(attachment)
        # TODO?: check that EntNum matches the company?
        soda_ref = self._get_soda_ref(soda_xml)
        existing_move = self.env["account.move"].search([("soda_ref", "=", soda_ref)])
        if existing_move:
            msg = _(
                "This file has already been imported. Please check SODA references."
            )
            raise UserError(msg)
        vals = {
            "ref": soda_ref,
            "soda_ref": soda_ref,
            "journal_id": self.id,
            "line_ids": [],
            "date": self._get_soda_date(soda_xml),
        }
        if self.company_id.soda_auto_map:
            self._soda_auto_map_accounts(soda_xml)
        missing_codes = []
        soda_mapping = self._get_account_soda_mapping()

        for line_xml in soda_xml.findall(".//Accounting"):
            code = line_xml.find("./Account").text
            name = line_xml.find("./Label").text
            account_id = soda_mapping.get(code)
            if not account_id:
                missing_codes.append(code)
            vals_line = {
                "account_id": account_id,
                "name": name,
                "debit": float(line_xml.find("./Amount/Debit").text),
                "credit": float(line_xml.find("./Amount/Credit").text),
            }
            vals["line_ids"].append((0, 0, vals_line))
        if missing_codes:
            msg = _("The following codes are missing: %s.")
            msg_end = _("Please create the SODA mappings in the Chart of Accounts.")
            raise UserError("\n\n".join([msg, msg_end]) % missing_codes)
        if move:
            move.write(vals)
        else:
            move = self.env["account.move"].create(vals)
            attachment.write({"res_model": "account.move", "res_id": move.id})
        return move

    def _get_account_soda_mapping(self):
        domain = [("soda_mapping", "!=", False)]
        accounts = self.env["account.account"].search(domain)
        soda_mapping = {}
        for account in accounts:
            codes = account.soda_mapping.split(",")
            for code in codes:
                soda_mapping[code] = account.id
        return soda_mapping

    def _get_soda_ref(self, soda_xml):
        source = soda_xml.find(".//Source").text
        seq_number = soda_xml.find(".//SeqNumber").text
        account_period = soda_xml.find(".//AccountPeriod").text
        return f"{source}/{seq_number}/{account_period}"

    def _get_soda_date(self, soda_xml):
        # we could return a date, but if GenDate is there it will be iso string
        # so let's stay consistent
        return soda_xml.findtext(".//GenDate") or fields.Date.today().isoformat()

    def _soda_auto_map_accounts(self, soda_xml):
        soda_mapping = self._get_account_soda_mapping()

        missing_codes = {}
        for line_xml in soda_xml.findall(".//Accounting"):
            code = line_xml.find("./Account").text
            if code not in soda_mapping:
                missing_codes[code] = line_xml.find("./Label").text

        domain = [("code", "in", list(missing_codes))]
        existing_accounts = self.env["account.account"].search(domain)
        account_by_code = {account.code: account for account in existing_accounts}
        to_create = []
        for code in missing_codes:
            account = account_by_code.get(code)
            if account:
                soda_mapping = code
                if account.soda_mapping:
                    soda_mapping = ",".join([account.soda_mapping, code])
                account.soda_mapping = soda_mapping
            else:
                vals_account = {
                    "code": code,
                    "name": missing_codes[code],
                    "soda_mapping": code,
                }
                to_create.append(vals_account)
        if to_create:
            self.env["account.account"].create(to_create)

    def _get_move_action(self, moves):
        xml_id = "account.action_move_journal_line"
        action = self.env["ir.actions.actions"]._for_xml_id(xml_id)
        vals = {"context": {}, "domain": [("id", "in", moves.ids)]}
        if len(moves) == 1:
            vals["view_mode"] = "form"
            vals["views"] = [[False, "form"]]
            vals["res_id"] = moves.id
        action.update(vals)
        return action
