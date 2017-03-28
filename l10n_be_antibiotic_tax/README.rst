.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Belgium Antibiotic Taxes
========================

This is a data module which extends the l10n_be chart of taxes
to support Antibiotics Taxes.

Installation
============

There is no specific installation procedure for this module.

Configuration
=============

If you install this module after instanciating the chart of account
for your company, it is recommanded to use the account_chart_update
module from the OCA/account-financial-tools repository .

You may also need to customize your invoice layout to render
these antibiotic taxes in the desired way.

Usage
=====

To use this module, you need to add the antibiotic
taxes on the products which are subjected to these rules:

* https://www.fagg-afmps.be/fr/veterinaire/medicaments/medicaments/distribution/taxe_antibiotique

You must make sure that the sequences of the ANTIOTIC taxes
is smaller than the sequences of the VAT taxes so the VAT is correctly
computed on top of the ANTIBIOTIC taxes. The sequences are correct
when using l10n_be_taxes.

The module also define a specific tax code template for antibiotic taxes which
may help in reporting, and specific expense and income account templates.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/9.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* N/A

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-belgium/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
