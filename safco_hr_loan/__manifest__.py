# -*- coding: utf-8 -*-

{
    'name': 'Loan Management',
    'version': '12.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests and deductions of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Aymen RAHMANI",
    'maintainer': 'Aymen RAHMANI',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        'views/hr_payroll.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
