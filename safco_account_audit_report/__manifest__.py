# -*- coding: utf-8 -*-
{
    'name': 'Safco Accounting : Audit report',
    'version': '19.0.0.0.1',
    'category': 'Accounting ',
    'description': "Safco accounting audit report ",
    'author': "Aymen RAHMANI",
    'depends': ['account'],
    'data': [
            'views/view_res_partner.xml',
            'views/view_res_company.xml',
            'wizard/audit_report_wizard.xml',

            #'report/report.xml',
            'report/audit_report_print.xml',

            'security/ir.model.access.csv',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
