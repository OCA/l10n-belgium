This module allows you to import your bank transactions with a standard
**CODA** file (you'll find samples in the 'data' folder).

This module was renamed in v14 to follow the behavior of the parent OCA module account_statement_module.

This is an alternative to the l10n_be_coda module in Odoo Enterprise.
It uses the external python lib `pycoda <https://pypi.python.org/pypi/pycoda>`__ as parser.

Expected benefits:

* The pycoda parser is a better-tested external python lib.
* Better separation between file parsing and mapping of these data in Odoo.
* The module only depends of account_bank_statement_import.
