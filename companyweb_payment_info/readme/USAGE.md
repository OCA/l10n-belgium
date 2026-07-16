Configuration
-------------
1. Set up your Companyweb credentials under Contacts > Companyweb > Settings.
2. Go to Settings > Companyweb > Payment Info and enable
   **Send Open Invoices to Companyweb** for your company (enabled by default).

The scheduled action **Companyweb: Send Open Invoices** runs once per day and
submits all posted, unpaid customer invoices to Companyweb. Invoices for
customers without a VAT number or company registry number, or in unsupported
countries, are skipped silently.

The result of each submission is logged as an info message, including the number
of valid and invalid invoices processed and the total open amount reported.
