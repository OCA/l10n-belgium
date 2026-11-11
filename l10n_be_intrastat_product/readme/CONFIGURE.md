- Accounting -\> Configuration -\> Settings

  Section Intrastat:

  - Arrivals : Exempt, Standard or Extended
  - Dispatches : Exempt, Standard or Extended
  - Default Intrastat Transport Mode (Required for Extended Declaration)
  - Default Intrastat Region

  Section Customer Invoices:

  - Default Incoterm

- Warehouse

  Intrastat Region to cope with warehouses in different regions

- Inrastat Codes, Supplementary Units, Transaction Tyoes, Transport
  Modes, Regions

  Cf. menu Accounting / Configuration / Intrastat

  The configuration data is loaded when installing the module. We do not
  recommend to change these settings.

  A configuration wizard (part of the **intrastat_product** module) also
  allows to update the Intrastat Codes so that you can easily
  synchronise your Odoo instance with the latest list of codes supplied
  by the configuration wizard. (an update is published on an annual
  basis by the Belgian National Bank).

- Product

  You can define a default Intrastat Code on the Product or the Product
  Category.

- Fiscal Positions

  Check your Fiscal Positions and set the 'Intrastat' field for
  transactions that must be included in the intrastat declaration. We
  recommend to set the 'VAT required' flag on the 'Intra Community
  Regime' Fiscal Position for B2B customers.

  If you have B2C customers or B2B customers which are not subject to
  VAT you can create a 'Intra Community Regime NA' Fiscal Position on
  which the 'Intrastat' field is set to B2C while the 'VAT required'
  flag has been turned off.

- Partner

  Ensure that your B2B Customer records have a valid VAT Number.

  Consider the use of the OCA **account_fiscal_position_vat_check
  module** to enforce the correct setting. Cf.
  <https://github.com/OCA/account-financial-tools>.
