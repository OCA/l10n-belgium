# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import datetime
from dateutil import parser as date_parser
from coda.parser import Parser
from coda.statement import AmountSign, MovementRecordType

from account_statement_base_import.parser.file_parser \
    import BankStatementImportParser
from _collections import deque


class CodaFileParser(BankStatementImportParser):

    """
    CODA parser that use a define format in coda to import
    bank statement.
    """
    parser_name = 'coda_transaction'

    def __init__(self, parse_name, parser=Parser(), *args, **kwargs):
        self._parser = parser
        self._statement = None
        super(CodaFileParser, self).__init__(parse_name, *args, **kwargs)
        self.support_multi_statements = True

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is coda_transaction
        """
        return parser_name == cls.parser_name

    @property
    def statement(self):
        """
        Return the statement. The statement is only available after a call
        to the ''parse'' method
        """
        return self._statement

    def _custom_format(self, *args, **kwargs):
        """
        No other work on data are needed in this parser.
        """
        return True

    def _pre(self, *args, **kwargs):
        """
        Launch the parsing through the CODA Parser
        """
        self._statements = deque(self._parser.parse(self.filebuffer))
        return True

    def _parse(self, *args, **kwargs):
        """
        Set the parser on the next statement parsed in the file.
        Return true if a  statement has been found, false otherwise
        """
        if len(self._statements):
            self._statement = self._statements.popleft()
            self.result_row_list = []
            for statement_line in self._statement.movements:
                if statement_line.type != MovementRecordType.GLOBALISATION:
                    self.result_row_list.append(statement_line)
            return True
        return False

    def _validate(self, *args, **kwargs):
        """
        No validation needed for this parser
        """
        return True

    def get_st_vals(self):
        """
        This method return a dict of vals that can be passed to
        create method of statement.
        :return: dict of vals that represent additional infos for the statement
            found in the file.
            {
             'name': paper_seq_number
             'balance_start': balance_start,
             'balance_end_real': balance_end_real
            }
        """
        balance_start = self.statement.old_balance
        if self.statement.old_balance_amount_sign == AmountSign.DEBIT:
            balance_start = - balance_start
        balance_end_real = self.statement.new_balance
        if self.statement.new_balance_amount_sign == AmountSign.DEBIT:
            balance_end_real = - balance_end_real
        vals = {'balance_start': balance_start,
                'balance_end_real': balance_end_real,
                'date': self.statement.creation_date
                }
        name = self.statement.paper_seq_number
        if name:
            year = ""
            if self.statement.creation_date:
                parsed_date = date_parser.parse(self.statement.creation_date)
                year = "%s/" % parsed_date.year
            vals.update({
                'name': "%s%s" % (year, self.statement.paper_seq_number),
                })
        return vals

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the responsibility
        of every parser to give this dict of vals, so each one can implement his
        own way of recording the lines.
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
        return {'name': "\n".join(filter(None, [line.counterparty_name,
                                                line.communication,
                                                line.payment_reference])),
                'date': line.entry_date or datetime.datetime.now().date(),
                'amount': amount,
                'ref': line.ref,
                'note': line.counterparty_name or None,
                'partner_acc_number': line.counterparty_number or None,
                }


class L10NBECodaFileParser(CodaFileParser):
    """
    CODA parser that use a define format in coda to import
    bank statement as defined by the l10n_be_coda module.
    """

    parser_name = 'l10n_be_coda_transaction'

    def __init__(self, parse_name, parser=Parser(), *args, **kwargs):
        self._parser = parser
        self._statement = None
        super(L10NBECodaFileParser, self).__init__(parse_name, *args, **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is l10n_be_coda_transaction
        """
        return parser_name == cls.parser_name

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method add to field coda_account_number to values from the base
        parser
        """
        vals = CodaFileParser.get_st_line_vals(self, line, args, kwargs)
        vals.update({
            # in case l10n_be_coda is installed
            'coda_account_number': line.counterparty_number or None,
        })
        return vals
