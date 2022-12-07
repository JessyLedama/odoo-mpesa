# -*- coding: utf-8 -*-
{
    'name': "Mpesa Accounting",

    'summary': """
        Adds Mpesa features to accounting module""",

    'description': """
        Allows viewing of Mpesa transactions on Accounting module
    """,

    'author': "Tritel Technologies Ltd",
    # 'website': "http://www.yourcompany.com",

    'category': 'Accounting',
    'version': '0.1',

    'depends': ['base', 'account_accountant', 'account_followup'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

}