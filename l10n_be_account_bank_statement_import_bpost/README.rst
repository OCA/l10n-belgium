.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Import Bpost CSV bank statements
================================

This module allows you to import the CSV bank statement files from Bpost
(www.bpost.be) in Odoo.

The structure of the Bpost's CSV bank statement is the following:

The first line of Bpost's CSV bank statement contains the bank account number, like this::

    "Numéro de compte :";"000-9431621-60";"Compte Postcheque";;;;;;;;

The second line contains the title of the columns::

    "Numéro d'opération";"Date de l'opération";"Description";"Montant de l'opération";"Devise";"Date valeur";"Compte de contrepartie";"Nom de la contrepartie";"Communication 1";"Communication 2";"Référence de l'opération"

The next lines contain the statement lines::

    "0000001";"19-09-2015";"Virement en votre faveur";"+94,00";"EUR";"19-09-2015";"843-2305042-42";"ALEXIS DE LATTRE";"Don pour OCA";;"B6A14XM03B029170"


Installation
============

This module depends on the module *account_bank_statement_import* which
is available:

* for Odoo version 8: in the OCA project `bank-statement-import <https://github.com/OCA/bank-statement-import>`
* for Odoo version 9: it is an official module.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-belgium/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/l10n-belgium/issues/new?body=module:%20l10n_be_account_bank_statement_import_bpost%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
