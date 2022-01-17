import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-l10n-belgium",
    description="Meta package for oca-l10n-belgium Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-account_bank_statement_import_coda',
        'odoo13-addon-companyweb_base',
        'odoo13-addon-companyweb_payment_info',
        'odoo13-addon-l10n_be_mis_reports',
        'odoo13-addon-l10n_be_partner_identification',
        'odoo13-addon-l10n_be_partner_kbo_bce',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
