# -*- coding: utf-8 -*-


{
    'name': 'HR Safco',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'description': 'Adding saudi market required extra Fields In employee profile.',
    'author': 'Aymen RAHMANI',
    'maintainer': 'Aymen RAHMANI',
    'depends': ['base', 'hr','hr_payroll', 'mail','hr_holidays','hr_contract','hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron.xml',
        'data/hr_contract_sequence.xml',

        'views/hr_attendance_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_run.xml',
        'views/view_resource_calendar.xml',
        'views/hr_employee_view.xml',
        #

        'wizard/normalize_attendences_views.xml',
        #'wizard/adjust_attendences_view.xml',
        #'views/view_leave_refuse_reason_form.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}

