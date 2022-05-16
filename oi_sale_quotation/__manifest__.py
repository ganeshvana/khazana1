# -*- coding: utf-8 -*-

{
    'name': 'REPORT Form',
    'category': 'REPORT',
    'summary': 'Basic REPORT form',
    'version': '15.0',
    'author': 'oodu implementers ',
    'description': """""",
    'depends': ['base', 'sale', 'stock', 'sale_term', 'purchase'],
    'application': True,
    'data': [
        
        'views/report_templates_quotations.xml',
        'views/report_quotation.xml',
        'views/report_templates_delivery.xml',
        'views/report_delivery.xml',
         'views/report_template_return.xml',
        'views/report_return.xml',
         'views/report_template_inward.xml',
        'views/report_inward.xml',
        'views/report_template_material.xml',
        'views/report_material.xml',
        'views/inventory_inherit_view.xml',
        'views/report_purchase.xml',
        'views/report_templates_purchase.xml',


      
    ],
}
