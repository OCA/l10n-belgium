.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Companyweb - Know who you are dealing with
==========================================

This module provides access to financial health information about Belgian
companies right from the Customer form. Information is obtained
from the Companyweb database (www.companyweb.be).

Main Features
-------------
* Obtain crucial information about Belgian companies,
  based on their VAT number: name, address,
  credit limit, health barometer, financial informations
  such as turnover or equity capital, and more.
* Fetch or update name, address and credit limit of your customers.
* Follow a list of customers and automatically receive updates.
* Generate reports about payment habits of your customers.
* Access to detailed company information on www.companyweb.be.

Installation
============
This module depends on module account_financial_report_webkit which
provides an accurate algorithm for open invoices report.

Usage
=====

You must have a Companyweb account to use this module in production.
Please visit www.companyweb.be and use login 'cwacsone',
with password 'demo' to obtain test credentials.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/119/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/{project_repo}/issues/new?body=module:%20{module_name}%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------
* Jacques-Etienne Baudoux <je@bcim.be> (BCIM sprl)
* Sylvain Van Hoof <sylvain@okia.be>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Adrien Peiffer <adrien.peiffer@acsone.eu>

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
