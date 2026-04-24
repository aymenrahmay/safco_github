
{
    'name': 'Loan Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage employee loan requests and payroll deductions',
    'description': 'Helps you manage loan requests and deductions for your company staff.',
    'category': 'Human Resources/Payroll',
    'author': 'Aymen RAHMANI',
    'maintainer': 'Aymen RAHMANI',

    'depends': ['base', 'hr_payroll', 'hr', 'account', 'l10n_sa_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/salary_rule_loan.xml',
        'views/hr_loan.xml',
        #'views/hr_payroll.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
