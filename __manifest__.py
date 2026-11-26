# -*- coding: utf-8 -*-
{
    'name': 'Office Asset Loan',
    'version': '19.0.1.0.0',
    'summary': 'Simple and robust internal office asset and inventory loan management',
    'sequence': 1,
    'description': """
Office Asset Loan
=================
This module manages internal office inventory items (projectors, spare laptops, cameras, cables, etc.)
and tracks their borrowing lifecycle:
- Asset registration with unique asset codes and condition tracking.
- Loan requests with automated sequence numbering (LOAN/0001).
- Workflow stages: Draft -> Borrowed -> Returned / Cancelled.
- Automated validation preventing double-borrowing and damaged asset checkout.
- Overdue tracking and duration calculation.
    """,
    'category': 'Tools',
    'author': 'Noval',
    'website': 'https://github.com/NovalAsidiqFirdaus/Office-Asset-Loan',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/office_asset_security.xml',
        'data/office_asset_loan_sequence.xml',
        'views/office_asset_views.xml',
        'views/office_asset_loan_views.xml',
        'views/office_asset_menus.xml',
    ],
    'demo': [
        'demo/office_asset_loan_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

