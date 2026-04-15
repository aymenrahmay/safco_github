# -*- coding: utf-8 -*-
{
    'name': 'Multiple Invoice Payment',
    'summary': '''
        Multiple invoices full / partial payment on single payment screen.''',
    'description': '''
        Module allows you to select multiple invoices to pay on payment form. 
        Invoices can be selcted on customer payments and vendor payments. 
        This modules supports partial payment for multiple invoices on single payment screen.
        Multi invoice,easy payment,like version 8, 9,multipile invoice,Multupile,Invoice,Payment,Payment invoice, multipile,
        multipile invoice, payment invoice,Multipile Payment,Payment, multipile, invoice multipile, odoo invoice, invoice odod, multipile odoo invoice,
        customer invoice, Customer Invoice, MULTIPILE, INVOICE, MULTIPILE INVOICE, ODOO MULTIPILE INVOICE, invoice, multipile  ''',
    'version': '19.0.1.0.0',
    'live_test_url': 'https://youtu.be/Xrh48sca9xw',
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'company': 'Geo Technosoft',
    'sequence': 1,
    "category": "Accounting",
    'depends': ['account','safco_sales'],
    'data': [
        "security/ir.model.access.csv",
        'views/account_payment_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'price': 26,
    'currency':'USD',
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
