# -*- coding: utf-8 -*-
# © 2015-2018 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
from tempfile import NamedTemporaryFile
from datetime import datetime
from openerp import models, fields, api, _
logger = logging.getLogger(__name__)

try:
    import unicodecsv
except ImportError:
    logger.debug('Cannot import unicodecsv')


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    @api.model
    def _check_bpost(self, data_file):
        if (
                len(data_file) >= 66 and
                'ro de compte' in data_file[3:66] and
                'Post' in data_file[3:66]):
            return True
        else:
            return False
        # The file starts with <U+FEFF> = UTF-8 BOM
        # http://en.wikipedia.org/wiki/Byte_order_mark

    @api.model
    def _parse_file(self, data_file):
        """ Import a file in Bpost CSV"""
        bpost = self._check_bpost(data_file)
        if not bpost:
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)
        transactions = []
        i = 0
        account_number = currency_code = False
        diff = 0.0
        # Write to file and re-open with 'U' option
        fileobj = NamedTemporaryFile('w+')
        fileobj.write(data_file)
        fileobj.seek(0)
        fu = open(fileobj.name, 'rU')
        for line in unicodecsv.reader(fu, encoding='utf-8', delimiter=';'):
            i += 1
            logger.debug("Line %d: %s", i, line)
            if i == 1:
                account_number = line[1].replace('-', '')
            if i < 3:
                continue  # skip 2 first lines
            if not line:
                continue
            name = line[2].strip()
            if line[7] and line[7].strip():
                name = '%s - %s' % (name, line[7].strip())
            if line[8] and line[8].strip():
                name = '%s - %s' % (name, line[8].strip())
            date = datetime.strptime(line[1], '%Y-%m-%d')
            # In Bpost CSV file : decimal separator = ,
            # thousand separator = .
            amount = float(line[3].replace('.', '').replace(',', '.'))
            diff += amount
            currency_code = line[4]
            ref = line[9]
            vals_line = {
                'date': date,
                'name': name,
                'ref': ref,
                'unique_import_id': '%s-%s-%s' % (
                    fields.Date.to_string(date), amount, ref),
                'amount': amount,
                'partner_name': line[8],
                'account_number': line[7],
                }
            transactions.append(vals_line)
        fu.close()
        fileobj.close()

        vals_bank_statement = {
            'name': _('Bpost %s') % account_number,
            'balance_start': 0,
            'balance_end_real': 0 + diff,
            'transactions': transactions,
            }
        return currency_code, account_number, [vals_bank_statement]
