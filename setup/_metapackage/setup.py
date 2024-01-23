import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_statement_import_coda>=16.0dev,<16.1dev',
        'odoo-addon-companyweb_base>=16.0dev,<16.1dev',
        'odoo-addon-companyweb_payment_info>=16.0dev,<16.1dev',
        'odoo-addon-l10n_be_bpost_address_autocomplete>=16.0dev,<16.1dev',
        'odoo-addon-l10n_be_mis_reports>=16.0dev,<16.1dev',
        'odoo-addon-l10n_be_mis_reports_xml>=16.0dev,<16.1dev',
        'odoo-addon-l10n_be_partner_identification>=16.0dev,<16.1dev',
        'odoo-addon-l10n_be_partner_kbo_bce>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
