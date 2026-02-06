# -*- coding: utf-8 -*-
# Copyright 2015-today Geo Technosoft (<http://www.geotechnosoft.com>)

{
    'name': 'GTS Aged Partner Pivot Report',
    'summary': 'Aged Pivot Report Odoo',
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'category': 'Accounting',
    'version': '16.0.0.1',
    'live_test_url': 'https://youtu.be/5ixwlgc1Bwc',
    'description': """
        This module provide feature to view Aged Partner Balance report in pivot view in odoo.
        Aged Partner Report odoo , Aged Report Financial report , Aged Receivable report , 
        Aged Payable report, gts_aged_pivot_report,gtsagedpivotreport,gts aged pivot report
    """,
    'sequence': 2,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/aged_receivable_wiz_view.xml',
        'wizard/aged_payable_wiz_view.xml',
        'wizard/bank_report_wiz_view.xml',
        'report/aged_receivable_report_view.xml',
        'report/aged_payable_report_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'price': 19.00,
    'currency':'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
