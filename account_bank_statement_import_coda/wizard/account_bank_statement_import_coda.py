# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import datetime
import logging
from dateutil import parser as date_parser

from odoo import api, models, _
from odoo.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)

try:
    from coda.parser import Parser
    from coda.statement import AmountSign, MovementRecordType
except ImportError:
    _logger.error(
        "CODA parser unavailable because the `pycoda` Python library cannot "
        "be found. It can be downloaded and installed from "
        "`https://pypi.python.org/pypi/pycoda`.")
    Parser = None


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _check_coda(self, data_file):
        if Parser is None:
            return False
        try:
            # Matches the first 24 characters of a CODA file, as defined by
            # the febelfin specifications
            return re.match(rb'0{5}\d{9}05[ D] {7}', data_file) is not None
        except:
            return False

    @api.model
    def _parse_file(self, data_file):
        if not self._check_coda(data_file):
            return super()._parse_file(data_file)
        vals_bank_statements = []
        try:
            statements = Parser().parse(data_file)
            for statement in statements:
                vals_bank_statements.append(
                    self.get_st_vals(statement))
        except Exception as e:
            _logger.exception('Error when parsing coda file')
            raise UserError(
                _("The following problem occurred during import. "
                  "The file might not be valid.\n\n %s" % e.message))

        acc_number = None
        currency = None
        if statements:
            acc_number = statements[0].acc_number
            currency = statement.currency
        return currency, acc_number, vals_bank_statements

    def get_st_vals(self, statement):
        """
        This method return a dict of vals that can be passed to
        create method of statement.
        :return: dict of vals that represent additional infos for the statement
            found in the file.
            {
             'name': paper_seq_number
             'balance_start': balance_start,
             'balance_end_real': balance_end_real,
             'transactions': transactions
            }
        """
        balance_start = statement.old_balance
        if statement.old_balance_amount_sign == AmountSign.DEBIT:
            balance_start = - balance_start
        balance_end_real = statement.new_balance
        if statement.new_balance_amount_sign == AmountSign.DEBIT:
            balance_end_real = - balance_end_real
        transactions = []
        statement_date = statement.new_balance_date
        vals = {
            'balance_start': balance_start,
            'balance_end_real': balance_end_real,
            'date': statement_date,
            'transactions': transactions
        }
        name = statement.paper_seq_number
        if name:
            year = ""
            if statement_date:
                parsed_date = date_parser.parse(statement_date)
                year = "%s/" % parsed_date.year
            vals.update({
                'name': "%s%s" % (year, statement.paper_seq_number),
            })

        globalisation_dict = dict([
            (st.ref_move, st) for st in statement.movements
            if st.type == MovementRecordType.GLOBALISATION])
        information_dict = {}
        # build a dict of information by transaction_ref. The transaction_ref
        # refers to the transaction_ref of a movement record
        for info_line in statement.informations:
            infos = information_dict.setdefault(info_line.transaction_ref, [])
            infos.append(info_line)

        for sequence, line in enumerate(
                filter(lambda l: l.type != MovementRecordType.GLOBALISATION,
                       statement.movements)):
            info = self.get_st_line_vals(line,
                                         globalisation_dict,
                                         information_dict)
            info['sequence'] = sequence
            transactions.append(info)
        return vals

    def get_st_line_note(self, line, information_dict):
        """This method returns a formatted note from line information
        """
        note = []
        if line.counterparty_name:
            note.append(_('Counter Party') + ': ' +
                        line.counterparty_name)
        if line.counterparty_number:
            note.append(_('Counter Party Account') + ': ' +
                        line.counterparty_number)
        if line.counterparty_address:
            note.append(_('Counter Party Address') + ': ' +
                        line.counterparty_address)
        infos = information_dict.get(line.transaction_ref, [])
        if line.communication or infos:
            communications = []
            if line.communication:
                communications.append(line.communication)
            for info in infos:
                communications.append(info.communication)
            note.append(_('Communication') + ': ' +
                        " ".join(communications))
        return note and '\n'.join(note) or None

    def get_st_line_name(self, line, globalisation_dict):
        """
        This method must return a valid name for the statement line
        The name is the statement communication if exists or
        the communication of the related globalisation line if exists or
        '/'
        """
        name = line.communication
        if not name and line.ref_move in globalisation_dict:
            name = globalisation_dict[line.ref_move].communication
        return name or '/'

    def get_st_line_vals(self, line, globalisation_dict, information_dict):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals,
        so each one can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
            result_row_list
            :return: dict of values to give to the create method of
            statement line,
                     it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                }
        """
        amount = line.transaction_amount
        if line.transaction_amount_sign == AmountSign.DEBIT:
            amount = - amount
        return {
            'name': self.get_st_line_name(line, globalisation_dict),
            'date': line.entry_date or datetime.datetime.now().date(),
            'amount': amount,
            'ref': line.ref,
            'partner_name': line.counterparty_name or None,
            'account_number': line.counterparty_number or None,
            'note': self.get_st_line_note(line, information_dict),
            'unique_import_id': line.ref + line.transaction_ref,
        }

    @api.model
    def _complete_statement(self, stmts_vals, journal_id, account_number):
        stmts_vals = super()._complete_statement(
            stmts_vals, journal_id, account_number)
        journal = self.env['account.journal'].browse(journal_id)
        stmts_vals['name'] = '%s/%s' % (journal.code, stmts_vals['name'])
        return stmts_vals
