* Accounting -> Configuration -> Settings

  - Arrivals : Exempt, Standard or Extended
  - Dispatches : Exempt, Standard or Extended
  - Default Intrastat Region
  - Default Intrastat Transaction
  - Default Intrastat Transport Mode (Extended Declaration)
  - Default Intrastat Incoterm (Extended Declaration)

* Warehouse

  Intrastat Region to cope with warehouses in different regions

* Inrastat Codes, Supplementary Units, Transaction Tyoes, Transport Modes, Regions

  Cf. menu Accounting / Configuration / Intrastat

  The configuration data is loaded when installing the module.
  We recommend no to change these settings.

  A configuration wizard also allows to update the Intrastat Codes so that you can easily
  synchronise your Odoo instance with the latest list of codes supplied with this module
  (an update is published on an annual basis by the Belgian National Bank).

* Product

  You can define a default Intrastat Code on the Product or the Product Category.

* Fiscal Positions

  Check your Fiscal Positions and set the 'Intrastat' flag for transactations that
  must be included in the intrastat declaration.
  We recommend to set the 'VAT required' flag on the 'Intra Community Regime' Fiscal Position.

  If you have B2C customers or B2B customers which are not subject to VAT you can create a
  'Intra Community Regime NA' Fiscal Position on which the 'Intrastat' flag is set while the 'VAT required'
  flag has been turned off.

* Partner

  Ensure that your B2B Customer records have a valid VAT Number.

  Consider the use of the OCA **account_fiscal_position_vat_check module** to enforce the correct setting.
  Cf. https://github.com/OCA/account-financial-tools.

  If you have not set the 'Detect Automatically' flan on your Intra Community Fiscal Position(s) than you should
  set the 'Intra Community Regime NA' Fiscal Position on B2B customer records who are not subject to VAT.
  Alternatively you can also set 'NA' in the VAT number field of such a customer.
