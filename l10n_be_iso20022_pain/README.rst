.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

l10n_be_iso20022_pain
=====================

This modules adds Belgium-specific support to OCA/bank-payment
payment initiation modules (account_banking_pain_base).

* support of the BBA structured communication type [1]

Reference information can be found in
* https://www.febelfin.be/fr/paiements/directives-et-protocoles-standards-bancaires
* https://www.febelfin.be/nl/betaalverkeer/richtlijnen-en-protocollen-bankstandaarden
* [1] https://www.febelfin.be/sites/default/files/Payments/AOS-OGMVCS.pdf

Installation
============

There is nothing specific to do to install this module,
except having the dependent modules available in your addon path.

It is recommended to install l10n_be_invoice_bba, and you will
probably want to use account_banking_sepa_credit_transfer and/or
account_banking_sepa_direct_debit.

Configuration
=============

None.

Usage
=====

This module adds a new 'Belgium BBA' communication types on payment lines.
When adding invoices to payment orders, invoices having this BBA communication type
automatically put the correct communication type on payment lines. Generated
PAIN files then use the correct communication type.

Known issues / Roadmap
======================

None.

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
