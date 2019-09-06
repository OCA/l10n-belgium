import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_bank_statement_import_coda',
        'odoo9-addon-l10n_be_antibiotic_tax',
        'odoo9-addon-l10n_be_apb_tax',
        'odoo9-addon-l10n_be_eco_tax',
        'odoo9-addon-l10n_be_iso20022_pain',
        'odoo9-addon-l10n_be_mis_reports',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
