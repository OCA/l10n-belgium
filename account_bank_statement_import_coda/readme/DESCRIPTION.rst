This module allows you to import your bank transactions with a standard
**CODA** file (you'll find samples in the 'data' folder).

This is an alternative to the l10n_be_coda module in Odoo Enterprise.

Expected benefits:

* The pycoda parser is a better-tested external python lib.
* Better separation between file parsing and mapping of these data in Odoo.
* The module only depends of account_bank_statement_import.
