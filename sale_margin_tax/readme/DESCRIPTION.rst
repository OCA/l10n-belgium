This module takes a simple approach to the Belgian margin tax.

https://finances.belgium.be/fr/entreprises/tva/assujettissement-tva/regime-imposition-marge

With this, the tax is due on the margin, that is to say the benefit made between the purchase price and the selling price of used goods (not taking into account any cost incurred in between, including refurbishing or repairing costs).

Note that the seller has to be able to track the purchasing price in their inventory.
There are different ways this can be done - by lot, serial number, retrieved from the purchase order, etc.
By default, this module assumes that the purchase price is the same as the cost encoded on the product.
This advanced behaviour can be implemented on overriding modules.

When such a tax is used, the actual tax amount has to be computed at invoicing time.
Moreover, the actual tax amount should be hidden from the report, and an obligatory note has to be present on the invoice.
