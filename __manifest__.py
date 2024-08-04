# -*- coding: utf-8 -*-
{
    'name': "Libro Mayor",

    'summary': """
        Libro Mayor para Odoo Community""",

    'description': """
        Libro Mayor para Odoo Community
    """,

    'author': "Mario Roberto",
    'website': "https://mrgomezsv.github.io/",

    'category': 'Accounting',
    'version': '0.1',

    'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'views/account_group.xml',
        'wizard/general_ledger.xml',
    ],
}
