# -*- coding: utf-8 -*-
{
    'name': "Pos Mpesa",

    'summary': """
        Integrates Mpesa Payment Method with the point of sale""",

    'description': """
        Allows payment (full or partial) of a point of sale order with 
        Mpesa.
        Avails a method to confirm the payment is registered on the system.
    """,

    'author': "Tritel Technologies Ltd",
    'website': "http://www.yourcompany.com",

    'category': 'POS',
    'version': '0.1',

    'depends': [
        'base',
        'point_of_sale',
        'accounting_mpesa'
        ],

    'data': [
        'views/assets.xml',
        'views/views.xml',
    ],
    'qweb': ['static/src/xml/pos_mpesa.xml'],
}