# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, exceptions, fields, models

from ..tools.codabox_api import CodaboxAPI

_logger = logging.getLogger(__name__)


class CodaboxFeed(models.Model):
    _name = "codabox.feed"
    _description = "Codabox feed"

    name = fields.Char("Client Name")
    identifier = fields.Integer("Identifier", index=True)
    client_uuid = fields.Char("Client UUID", index=True)
    client_code_uuid = fields.Char("Client Code UUID")
    fiduciary_uuid = fields.Char("Fiduciary UUID")
    feed_entry_ids = fields.One2many("codabox.feed.entry", "feed_id", "Feed Entries")

    @api.model
    def fetch_feed_data(self):
        """
        Fetches all the data from the CodaBox feeds
        """
        self.process_unimported_entries()
        codabox_api = CodaboxAPI(self.env)
        try:
            # Update the feed list
            codabox_api.get_feed_list()
        except Exception as excep:
            _logger.error(excep)

        feeds = self.search([])
        for feed in feeds:
            # Get all the feed entries
            try:
                codabox_api.fetch_feed_entries(feed.identifier)
            except Exception as excep:
                _logger.error(excep)

    @api.model
    def cron_fetch_feed(self):
        """
        Cron method that fetches for new feeds and fetches new feed entries
        """
        self.with_context(cron=True).fetch_feed_data()

    @api.model
    def process_unimported_entries(self):
        """
        Fetches all the unimported CODA entries already in the system and tries
        to import them again
        """
        for unimported_entry in self.env["codabox.coda.entry"].search(
            [("coda_file", "!=", False), ("statement_line_ids", "=", False)]
        ):
            try:
                unimported_entry.import_statement()
            except Exception as excep:
                _logger.error(excep)

    _sql_constraints = [
        ("feed_uniq", "unique(identifier)", "Feed identifier must be unique")
    ]


class CodaboxFeedEntry(models.Model):
    _name = "codabox.feed.entry"
    _rec_name = "index_uuid"
    _description = "Codabox Feed Entry"

    feed_id = fields.Many2one("codabox.feed", "Feed", required=True)
    index_uuid = fields.Char("Entry UUID", index=True, required=True)
    date = fields.Date("Date", required=True)
    document_model = fields.Selection(
        [
            ("coda", "Coda"),
            ("soda", "Soda"),
            ("purchase_invoice", "Purchase Invoice"),
            ("sales_invoice", "Sale Invoice"),
            ("expense", "Expense"),
        ],
        "Document Model",
        required=True,
    )
    xml_file = fields.Binary("XML File", attachment=True)
    xml_filename = fields.Char("XML Filename")

    _sql_constraints = [
        ("feed_entry_index_uniq", "unique(index_uuid)", "Feed index must be unique")
    ]


class CodaboxCodaEntry(models.Model):
    _name = "codabox.coda.entry"
    _inherits = {"codabox.feed.entry": "entry_id"}
    _rec_name = "index_uuid"
    _description = "Codabox Entry"

    entry_id = fields.Many2one(
        "codabox.feed.entry", "Entry", required=True, ondelete="cascade", index=True
    )
    movement_count = fields.Integer("Amount Of Movements")
    first_statement_number = fields.Integer("First Statement Number")
    last_statement_number = fields.Integer("Last Statement Number")
    iban = fields.Char("IBAN")
    bic = fields.Char("BIC")
    currency = fields.Char("Currency")
    coda_file = fields.Binary("CODA File", attachment=True)
    coda_filename = fields.Char("CODA Filename", compute="_compute_filename")
    statement_line_ids = fields.Many2many(
        "account.bank.statement.line", string="Bank Statements"
    )
    journal_id = fields.Many2one("account.journal", "Journal")

    @api.depends("iban", "date", "first_statement_number", "last_statement_number")
    def _compute_filename(self):
        """
        Computes the .CODA filename based on the iban and the date
        """
        for coda_entry in self:
            if coda_entry.coda_file:
                coda_entry.coda_filename = "%s_%s_%d-%d.CODA" % (
                    coda_entry.iban,
                    coda_entry.date,
                    coda_entry.first_statement_number,
                    coda_entry.last_statement_number,
                )
            else:
                coda_entry.coda_filename = ""

    def import_statement(self):
        """
        Import the CODA file as a bank statement using the import wizard
        """
        coda_entry_grouped_by_journal = {}
        for coda_entry in self.filtered(lambda e: e.coda_file):
            journal = self.env["account.journal"].search(
                [("bank_acc_number", "=", coda_entry.iban), ("type", "=", "bank")],
                limit=1,
            )
            if not journal:
                raise exceptions.Warning(
                    _("No bank journal found for %s. " "Please create one !")
                    % coda_entry.iban
                )

            if journal.id not in coda_entry_grouped_by_journal:
                coda_entry_grouped_by_journal[journal.id] = []

            coda_entry_grouped_by_journal[journal.id].append(coda_entry)

        for journal_id, coda_group in coda_entry_grouped_by_journal.items():
            StatementImport = self.env["account.bank.statement.import"]
            import_wizard = StatementImport.with_context(journal_id=journal_id).create(
                {"attachment_ids": []}
            )

            for entry in coda_group:
                import_wizard.attach_coda_file(entry)

            res = import_wizard.import_file()
            context = res.get("context")
            if context and context.get("statement_line_ids"):
                for entry in coda_group:
                    entry.write(
                        {
                            "journal_id": journal_id,
                            "statement_line_ids": [
                                (4, statement_line_id, 0)
                                for statement_line_id in context.get(
                                    "statement_line_ids"
                                )
                            ],
                        }
                    )
