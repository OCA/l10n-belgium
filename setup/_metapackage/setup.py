import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-l10n_be_antibiotic_tax',
        'odoo10-addon-l10n_be_apb_tax',
        'odoo10-addon-l10n_be_eco_tax',
        'odoo10-addon-l10n_be_iso20022_pain',
        'odoo10-addon-l10n_be_mis_reports',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
