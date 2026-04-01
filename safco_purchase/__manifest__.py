{
    'name': 'Safco Purchase',
    'version': '19.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Purchase and analytic account customizations for SAFCO',
    'description': 'Safco purchase customizations migrated to Odoo 19.',
    'author': 'Aymen RAHMANI',
    'license': 'LGPL-3',
    'depends': ['account', 'purchase', 'account'],
    'data': [
        'views/view_product.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
