
{
    "name": "OI CRM",
    "summary": "OI CRM",
    "version": "12.0.1",
    'category': 'CRM',
    "website": "",
	"description": """
		 	 
		 
    """,
	
    "author": "",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['base', 'stock','crm', 'sale_crm', 'helpdesk', 'purchase', 'product','website_sale_stock', 
                'website_sale', 'project', 'survey', 'account', 'l10n_in', 'website'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/wizard_views.xml',
        'view/crm.xml',
        'view/template.xml',
        'view/helpdesk.xml',
    ],
    
    'installable': True,
    'auto_install': True,    
       
}

