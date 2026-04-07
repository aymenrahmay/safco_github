# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    'name': 'Multiple Invoice Payment | Invoice Multi Payment | Invoice payments',
    'version': '19.0.1.1',
    'sequence':1,
    "category": 'Accounting' ,
    'description': """
App will allow multiple invoice payment from payment and invoice screen.
    """,
    'summary': 'multiple Invoice payments apps use to easy payment multi invoice ',
    'depends': ['sale_management','account'],
    'data': [
            'security/ir.model.access.csv',
            'views/account_payment.xml',
            'wizard/bulk_invoice_payment.xml',
            ],
	'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'https://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':45.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    "license":"LGPL-3",
    "pre_init_hook" :"pre_init_check",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
