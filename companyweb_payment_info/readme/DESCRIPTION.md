This module extends `companyweb_base` with a daily scheduled action that sends
all open customer invoices to Companyweb's AutoPayex API. Companyweb uses this
data to build an overview of how quickly companies pay their suppliers, which
helps businesses assess credit risk for new customers.

An invoice is considered open as long as it has not been fully paid. Partial
payments are supported: the remaining outstanding amount is reported. Credit
notes do not need to be submitted and are excluded automatically.

Only invoices for customers in supported countries with a known
VAT number or company registry number are submitted.

The following data is shared with Companyweb:

- Your company: VAT/registry number, country.
- Per invoice: customer VAT/registry number, country, invoice number, date,
  amount due.
