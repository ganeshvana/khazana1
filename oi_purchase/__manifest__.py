
{
    "name": "Purchase - Custom",
    "summary": "Purchase - Custom",
    "version": "12.0.1",
    'category': 'Purchase',
	"description": """
		 Purchase Custom	 
		 
    """,
	
    "author": "Oodu Implementers Private Limited",
    "website": "https://www.odooimplementers.com",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['base', 'purchase', 'quality'
    ],
    "data": [
            'security/ir.model.access.csv',            
            'view/purchase.xml',
            'view/configuration.xml',
    ],
    
    'installable': True,
    'auto_install': True,    
       
}

