
import itertools
from datetime import datetime, timedelta
from logging import getLogger

import requests

from odoo import api, fields, models

_logger = getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    real_check_in = fields.Datetime(string="Real check In")
    real_check_out = fields.Datetime(string="Real check Out")
    is_valid = fields.Boolean('Is valid ? ')
    is_normalized = fields.Boolean('Is normalized record ? ')
    manager_id = fields.Many2one('hr.employee', string="Employee manager", related='employee_id.parent_id', store=True, readonly=True)
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = 0.0

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        return True

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        return True

    def cron_get_attendences_from_remote_machines(self, specific_date=False):
        base_urls = ['http://13.50.1.24:80/']
        attendance_list = []
        for base_url in base_urls:
            attendance_data = self.get_data_from_devices(specific_date, base_url)
            if attendance_data:
                attendance_list.extend(attendance_data)
        if attendance_list:
            specific_date = fields.Date.today() if not specific_date else fields.Date.to_date(specific_date)
            specific_dt = fields.Datetime.to_datetime(specific_date)
            next_day = specific_dt + timedelta(days=1)
            attendance_records = self.env['hr.attendance'].search([('check_in', '>=', specific_dt), ('check_in', '<', next_day)])
            attendance_records.unlink()
            self.create_attendence_data(attendance_list)

    def create_attendence_data(self, attendence_list):
        sorted_attendance = sorted(attendence_list, key=lambda x: x['emp_code'])
        grouped_attendance = itertools.groupby(sorted_attendance, key=lambda x: x['emp_code'])
        for emp_code, emp_data in grouped_attendance:
            punch_times = [datetime.strptime(data['punch_time'], '%Y-%m-%d %H:%M:%S') for data in emp_data]
            employee_id, shall_work_from, shall_work_to, first_punch_time, last_punch_time = self.get_only_first_and_last_punch_time_with_shall_work(punch_times, emp_code)
            if employee_id and shall_work_from and shall_work_to:
                if first_punch_time and last_punch_time and first_punch_time.time() > datetime.strptime('14:00:00', '%H:%M:%S').time():
                    first_punch_time, last_punch_time = last_punch_time, first_punch_time
                check_in = shall_work_from + timedelta(hours=1)
                if first_punch_time:
                    check_in = shall_work_from if (first_punch_time - shall_work_from) < timedelta(minutes=15) else first_punch_time
                check_out = shall_work_to + timedelta(hours=-1)
                if last_punch_time:
                    authorized_check_out = shall_work_to - timedelta(minutes=15)
                    check_out = shall_work_to if last_punch_time > authorized_check_out else shall_work_to + timedelta(hours=-1)
                self.env['hr.attendance'].create({
                    'employee_id': employee_id.id,
                    'check_in': check_in - timedelta(hours=3) if check_in else check_in,
                    'check_out': check_out - timedelta(hours=3) if check_out else check_out,
                    'real_check_in': first_punch_time - timedelta(hours=3) if first_punch_time else first_punch_time,
                    'real_check_out': last_punch_time - timedelta(hours=3) if last_punch_time else last_punch_time,
                })

    def get_data_from_devices(self, specific_date, base_url):
        today = fields.Date.today()
        today_str = today.strftime('%Y-%m-%d') if not specific_date else str(specific_date)
        attendence_list = []
        token = False
        try:
            response = requests.post(
                base_url + 'jwt-api-token-auth/',
                json={'username': 'admin', 'password': 'admin'},
                headers={'Content-Type': 'application/json'},
                timeout=20,
            )
            response.raise_for_status()
            token = str(response.json().get('token') or '')
        except requests.exceptions.RequestException as exc:
            _logger.warning("Attendance device auth failed: %s", exc)

        if token:
            machine_urls = [base_url + f'iclock/api/transactions/?start_time={today_str} 00:00:00&end_time={today_str} 23:59:59&page_size=300']
            headers = {'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
            for device_url in machine_urls:
                try:
                    response = requests.get(device_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    for data in response.json().get('data', []):
                        attendence_list.append({'emp_code': data['emp_code'], 'punch_time': data['punch_time']})
                except requests.exceptions.RequestException as exc:
                    _logger.warning("Attendance device fetch failed: %s", exc)
        return attendence_list

    def get_shall_work_info(self, first_punch_time, day_num, resource_calendar_id):
        attendance = self.env['resource.calendar.attendance'].search([('dayofweek', '=', str(day_num)), ('calendar_id', '=', resource_calendar_id.id)], limit=1)
        if not attendance:
            return False, False
        shall_work_from = first_punch_time.replace(hour=int(attendance.hour_from), minute=0, second=0)
        shall_work_to = first_punch_time.replace(hour=int(attendance.hour_to), minute=0, second=0)
        return shall_work_from, shall_work_to

    def get_employee_resource_calendar_by_emp_code(self, emp_code):
        employee_id = False
        resource_calendar_id = False
        if emp_code:
            employee_id = self.env['hr.employee'].search([('identification_id', '=', emp_code)], limit=1)
            resource_calendar_id = employee_id.resource_calendar_id
        return employee_id, resource_calendar_id

    def get_only_first_and_last_punch_time_with_shall_work(self, punch_times, emp_code):
        if not punch_times:
            return False, False, False, False, False
        day_num = punch_times[0].weekday()
        first_punch_time = punch_times[0]
        last_punch_time = punch_times[-1]
        if first_punch_time == last_punch_time:
            last_punch_time = False
        employee_id, resource_calendar_id = self.get_employee_resource_calendar_by_emp_code(emp_code)
        if not employee_id or not resource_calendar_id:
            return employee_id, False, False, first_punch_time, last_punch_time
        shall_work_from, shall_work_to = self.get_shall_work_info(first_punch_time, day_num, resource_calendar_id)
        return employee_id, shall_work_from, shall_work_to, first_punch_time, last_punch_time
