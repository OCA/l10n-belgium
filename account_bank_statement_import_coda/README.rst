.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
      :alt: License: AGPL-3

==========================
Import CODA Bank Statement
==========================

This module allows you to import your bank transactions with a standard
**CODA** file (you'll find samples in the 'data' folder).

This is an alternative to the official l10n_be_coda that uses the 
external python lib pycoda_ as parser.

Expected benefits:

* The pycoda parser is a better-tested external python lib.
* Better separation between file parsing and mapping of these data in Odoo.
* The module only depends of account_bank_statement_import.

Installation
============

To install this module, you need to install the python library pycoda_.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/l10n-belgium/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Laurent Mignon <laurent.mignon@acsone.eu>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.

.. _pycoda: https://pypi.python.org/pypi/pycoda
