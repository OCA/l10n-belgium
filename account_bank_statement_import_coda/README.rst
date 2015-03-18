.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Import CODA Bank Statement
===========================

This module allows you to import your bank transactions with a standard
**CODA** file (you'll find samples in the 'data' folder).

This is an alternative to the official l10n_be_coda that uses the 
external python lib `pycoda <https://pypi.python.org/pypi/pycoda>`_
as parser.

Expected benefits:

* The pycoda parser is a better-tested external python lib.
* The module only depends of account_bank_statement_import (l10_be_coda on master branch depends of account_voucher, base_iban, l10n_be_invoice_bba, account_bank_statement_import)
* Better separation between file parsing and mapping of these data in Odoo.

Installation
============

To install this module, you need to install the python library
`pycoda <https://pypi.python.org/pypi/pycoda>`_

Credits
=======

Contributors
------------

* Laurent Mignon <laurent.mignon@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
