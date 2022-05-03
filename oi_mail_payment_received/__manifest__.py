# -*- coding: utf-8 -*-

{
    'name': "Payment Validation mail",
    'summary': "Send email when payment is posted",
    'description': "Send email when payment is posted",
    'version': "15.0.0.0",
    'category': "Accounting",
    'author': "Oodu Implementers Pvt. Ltd",
    'website': "https://www.odooimplementers.com",
    'depends': [
        'account'
    ],
    'data': [
        'data/email.xml',
        'views/res_config.xml',
    ],
    'application': False,
    'installable': True,
}
