.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Multilanguage alternative for the 'l10n_be' belgian accounting module.
======================================================================

This module activates the following functionality:

    * Support for the NBB/BNB legal Balance and P&L reportscheme including
      auto-configuration of the correct financial report entry when
      creating/changing a general account

Installation guidelines
=======================

In order to have the XBRL codes in the NBB/BNB legal reports, a patch must be installed on your Odoo instance (cf. https://github.com/odoo/odoo/pull/6923).
Install the diff file distributed with this module (cf. doc/account_financial_report.diff).

Credits
=======

Author
------
* Noviat <info@noviat.com>

Contributors
------------
* acsone <info@acsone.eu>
* Jacques-Etienne Baudoux <je@bcim.be>

Maintainer
----------
.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
