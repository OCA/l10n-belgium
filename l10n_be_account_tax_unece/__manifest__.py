# Copyright 2017-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n BE Account Tax UNECE",
    "summary": "Auto-configure UNECE params on Belgian taxes",
    "version": "12.0.1.0.0",
    "category": "Belgian Localization",
    "author": "Coop IT Easy SC,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-belgium",
    "license": "AGPL-3",
    "depends": ["l10n_be", "account_tax_unece"],
    "data": ["data/account_tax_template.xml"],
    "post_init_hook": "set_unece_on_taxes",
    "installable": True,
    "auto_installable": True,
}
