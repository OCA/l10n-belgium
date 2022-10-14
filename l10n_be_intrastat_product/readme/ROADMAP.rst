* The current version of the Belgian Intrastat reporting module is only based on invoices.
  Since associated stock moves are not taken into consideration, it is possible that manual
  corrections are required, e.g.
  Product movements without invoices are not included in the current version
  of this module and must be added manually to the report lines
  before generating the ONEGATE XML declaration.

* Credit Notes are by default assumed to be corrections to the outgoing or incoming
  invoices within the same reporting period. The product declaration values of the
  Credit Notes are as a consequence deducted from the declaration lines.
  You should encode the Credit Note with 'Intrastat Transaction Type = 21' when the goods
  returned.

* The current version of the Belgian Intrastat reporting module does not perform a
  cross-check with the VAT declaration.
