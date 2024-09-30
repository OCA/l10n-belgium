- The current version of the Belgian Intrastat reporting module is only
  based on invoices. Since associated stock moves are not taken into
  consideration, it is possible that manual corrections are required,
  e.g. Product movements without invoices are not included in the
  current version of this module and must be added manually to the
  report lines before generating the ONEGATE XML declaration.
- Refunds on invoices within the same reporting period are deducted from
  the declaration lines. No controls are executed on Refunds that are
  not linked to an invoice in the same reporting period. Such Refunds
  are reported under the default transaction code for refunds. It is
  recommend to manually set the correct transaction code while Credit
  Notes are created.
- The current version of the Belgian Intrastat reporting module does not
  perform a cross-check with the VAT declaration.
