import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-account_bank_statement_import_coda',
        'odoo8-addon-account_companyweb',
        'odoo8-addon-l10n_be_eco_tax',
        'odoo8-addon-l10n_be_iso20022_pain',
        'odoo8-addon-l10n_be_mis_reports',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
