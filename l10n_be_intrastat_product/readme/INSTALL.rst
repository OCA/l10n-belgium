Conflicting modules
~~~~~~~~~~~~~~~~~~~

This module conflicts with the module *report_intrastat* and *l10n_be_intrastat*
from the official addons.
If you have already installed these modules,
you should uninstall them before installing this module.

Refund handling
~~~~~~~~~~~~~~~

We recommend to also install the OCA stock_picking_invoice_link module,
cf. https://github.com/OCA/stock-logistics-workflow.
This modules establishes a link between invoice lines and stock pickings.
When this module is installed the declaration will take into account refunds created via return pickings.

Multi-company setup
~~~~~~~~~~~~~~~~~~~

Please ensure to set the Default Company of the OdooBot user to the company
for which you are installing this localization module.
Not doing so may result in a conflict with other localization modules (e.g. l10n_fr_intrastat_product).


Configuration wizard to load intrastat codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module comes with a configuration wizard that allows you to load the intrastat codes into the database.
The intrastat codes are available in 4 languages : english, dutch, french, german.

If your databases has been configured to support multiple languages, you should execute the wizard
for each language that you want to offer to the users.
