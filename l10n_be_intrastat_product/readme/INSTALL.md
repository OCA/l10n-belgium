## Conflicting modules

This module conflicts with the *account_intrastat* and
*l10n_be_intrastat* modules from the Odoo Enterprise addons. If you have
already installed these modules, you should uninstall them before
installing this module.

## Refund handling

We recommend to also install the OCA stock_picking_invoice_link module,
cf. <https://github.com/OCA/stock-logistics-workflow>. This modules
establishes a link between invoice lines and stock pickings. When this
module is installed the declaration will take into account refunds
created via return pickings.
