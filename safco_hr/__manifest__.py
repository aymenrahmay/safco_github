
{
    'name': 'HR Safco',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Saudi-specific HR, attendance, contract and payroll customizations',
    'description': "Adding saudi market required extra fields in employee profile and payroll flows.",
    'author': 'Aymen RAHMANI',
    'maintainer': 'Aymen RAHMANI',
    "license": "OPL-1",
    'depends': ['base', 'hr', 'hr_payroll', 'mail', 'hr_holidays', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron.xml',
        'views/hr_employee_view.xml',
        'views/hr_attendance_view.xml',
        #'views/hr_contract_view.xml',
    ],

    'installable': True,
    'application': False,
}
