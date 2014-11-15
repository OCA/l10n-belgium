# -*- coding: utf-8 -*-
#
#
# Authors: Laurent Mignon
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from openerp.addons.account_statement_coda_import.parser.coda_file_parser \
    import CodaFileParser
from openerp.addons.account_statement_coda_import.parser.coda_file_parser \
    import L10NBECodaFileParser


class AccountStatementProfil(Model):
    _inherit = "account.statement.profile"

    def _get_import_type_selection(self, cr, uid, context=None):
        """
        Has to be inherited to add parser
        """
        res = super(AccountStatementProfil, self)._get_import_type_selection(
            cr, uid, context=context)
        res.append((CodaFileParser.parser_name,
                    'CODA based transaction'))
        statement_line_obj = self.pool.get('account.bank.statement.line')
        if'coda_account_number' in statement_line_obj._columns:
            # True if l10n_be_coda is installed
            res.append((L10NBECodaFileParser.parser_name,
                        'CODA based transaction (L10nBECoda installed)'))
        return res

    def validate_statement(self, cr, uid, profile_id, parser, context=None):
        statement_info = parser.statement
        profile_obj = self.pool.get('account.statement.profile')
        profile = profile_obj.browse(cr, uid, profile_id, context=context)

        # Avoid importing statement for a different account number that the
        # one referencing the journal specified in the profile
        res_bank_obj = self.pool.get('res.partner.bank')
        acc_number = statement_info.acc_number
        ids = res_bank_obj.search_by_acc_number(cr,
                                                uid,
                                                acc_number,
                                                context=context)
        if len(ids) != 1:
            raise except_osv(_("Not supported CODA file"),
                             _("No matching Bank Account found for the "
                               "statement account number found in file %s")
                             % acc_number)
        res_bank = res_bank_obj.read(cr, uid, ids[0], {'journal_id', 'name'})
        if not res_bank.get('journal_id'):
            raise except_osv(_("Not supported CODA file"),
                             _("No Account Journal defined for bank account "
                               "named '%s' for account number '%s'")
                             % (res_bank.get('name'), acc_number))
        partner_journal_id, partner_journal_name = res_bank.get('journal_id')
        if profile.journal_id.id != partner_journal_id:
            raise except_osv(_("Not supported CODA file"),
                             _("The journal '%s' on the Bank Account '%s' "
                               "doesn't match the journal '%s' on the "
                               "profile") % (partner_journal_name,
                                             res_bank.get('name'),
                                             profile.journal_id.name))

    def prepare_statement_vals(self, cr, uid, profile_id, result_row_list,
                               parser, context=None):
        """
        Hook to build the values of the statement from the parser and
        the profile.
        """
        profile_obj = self.pool.get('account.statement.profile')
        profile = profile_obj.browse(cr, uid, profile_id, context=context)
        if profile.import_type in [CodaFileParser.parser_name,
                                   L10NBECodaFileParser.parser_name]:
            self.validate_statement(cr, uid, profile_id, parser, context)
        args = (cr, uid, profile_id, result_row_list, parser, context)
        return super(AccountStatementProfil, self)\
            .prepare_statement_vals(*args)
