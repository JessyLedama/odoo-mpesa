# -*- coding: utf-8 -*-

{
    'name': 'M-pesa Payment Gateway',
    'category': 'Hidden',
    'summary': 'Lipa na Mpesa Payment Gateway for E-commerce',
    'version': '8.0.1.0.0',
    'description': """Mpesa Payment Acquirer""",
    'author': 'Sunflower IT <dan@sunflowerweb.nl>',
    'depends': ['payment', 'website_sale',],
    'data': [
        'views/mpesa.xml',
        'views/payment_acquirer.xml',
        'views/assets_frontend.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
}