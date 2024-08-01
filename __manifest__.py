# -*- coding: utf-8 -*-
{
    'name': "Libro Mayor",

    'summary': """
        Libro Mayor para Odoo Community""",

    'description': """
        Libro Mayor para Odoo Community
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Accounting',
    'version': '0.1',

    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
