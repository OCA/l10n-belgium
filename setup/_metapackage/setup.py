import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_bank_statement_import_coda',
        'odoo12-addon-companyweb_base',
        'odoo12-addon-l10n_be_mis_reports',
        'odoo12-addon-l10n_be_mis_reports_xml',
        'odoo12-addon-l10n_be_partner_kbo_bce',
        'odoo12-addon-l10n_be_vat_reports',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
