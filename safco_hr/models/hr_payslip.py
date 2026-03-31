
from collections import defaultdict
from datetime import datetime, date, time, timedelta

import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    hr_payslip_run_total = fields.Float(compute='_compute_hr_payslip_run_total', string='Batch total')

    def _compute_hr_payslip_run_total(self):
        for run in self:
            run.hr_payslip_run_total = sum(run.slip_ids.mapped('net_wage'))


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    net_wage = fields.Float(compute='_compute_basic_net')
    requested_working_day = fields.Integer(compute='_compute_requested_working_days', store=True)

    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['account_id'] == account_id
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0))
            and ((not line_id.get('analytic_distribution') and not line.salary_rule_id.analytic_account_id.id and not line.slip_id.contract_id.analytic_account_id.id)
                 or (line_id.get('analytic_distribution') and (line.salary_rule_id.analytic_account_id.id in line_id['analytic_distribution'] or line.slip_id.contract_id.analytic_account_id.id in line_id['analytic_distribution'])))
        )
        return next(existing_lines, False)

    def _compute_basic_net(self):
        for payslip in self:
            net_line = payslip.line_ids.filtered(lambda line: line.code == 'NET')[:1]
            payslip.net_wage = net_line.total if net_line else 0.0

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_requested_working_days(self):
        for payslip in self:
            requested_working_day_based_on_dates = 0
            if payslip.date_from and payslip.date_to:
                date_from = fields.Date.to_date(payslip.date_from)
                date_to = fields.Date.to_date(payslip.date_to)
                current_date = date_from
                while current_date <= date_to:
                    if current_date.weekday() != 4:
                        requested_working_day_based_on_dates += 1
                    current_date += timedelta(days=1)
            leave_type_ids = self.env['hr.leave.type'].search([('time_type', '=', 'other')]).ids
            leave_records = self.env['hr.leave'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', 'in', ['confirm', 'validate', 'validate1']),
                ('date_from', '>=', payslip.date_from),
                ('date_to', '<=', payslip.date_to),
                ('holiday_status_id', 'in', leave_type_ids),
            ])
            total_number_of_days_display = sum(leave.number_of_days_display for leave in leave_records)
            payslip.requested_working_day = requested_working_day_based_on_dates - int(total_number_of_days_display)

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_worked_days_line_ids(self):
        if not self or self.env.context.get('salary_simulation'):
            return
        valid_slips = self.filtered(lambda p: p.employee_id and p.date_from and p.date_to and p.contract_id and p.struct_id)
        self.update({'worked_days_line_ids': [(5, 0, 0)]})
        generate_from_date = min(fields.Date.to_date(p.date_from) for p in self)
        current_month_end = date_utils.end_of(fields.Date.today(), 'month')
        generate_to_date = max(min(fields.Date.to_date(p.date_to), current_month_end) for p in self)
        generate_from = datetime.combine(generate_from_date, time.min)
        generate_to = datetime.combine(generate_to_date, time.max)
        self.mapped('contract_id')._generate_work_entries(generate_from, generate_to)
        for slip in valid_slips:
            if not slip.struct_id.use_worked_day_lines:
                continue
            slip.update({'worked_days_line_ids': slip._get_new_worked_days_lines()})

    def _attendance_fill_lines(self, lines, attendance_break_down):
        for _, worked_hours in attendance_break_down.items():
            lines['ATTN']['number_of_days'] += 1
            lines['ATTN']['number_of_hours'] += worked_hours

    def _attendance_create_lines(self, employee, contract, date_from, date_to):
        return {'ATTN': {'name': 'Attendance', 'sequence': 10, 'code': 'ATTN', 'number_of_days': 0.0, 'number_of_hours': 0.0, 'contract_id': contract.id}}

    def _attendance_domain(self, employee, contract, date_from, date_to):
        return [('employee_id', '=', employee.id), ('check_in', '>=', date_from), ('check_in', '<=', date_to)]

    def _attendance_get(self, employee, contract, date_from, date_to):
        return self.env['hr.attendance'].search(self._attendance_domain(employee, contract, date_from, date_to))

    def _attendance_hour_break_down(self, employee, contract, date_from, date_to):
        attns = self._attendance_get(employee, contract, date_from, date_to)
        day_values = defaultdict(float)
        for attn in attns:
            if not attn.check_out:
                raise ValidationError(_('This pay period must not have any open attendances.'))
            if attn.worked_hours:
                day_values[attn.check_in.isocalendar()] += attn.worked_hours
        return day_values

    def hour_break_down(self, code):
        self.ensure_one()
        if code == 'ATTN':
            return self._attendance_hour_break_down(self.employee_id, self.contract_id, self.date_from, self.date_to)
        parent = super()
        if hasattr(parent, 'hour_break_down'):
            return parent.hour_break_down(code)
        return {}

    def hours_break_down_week(self, code):
        days = self.hour_break_down(code)
        weeks = defaultdict(float)
        for isoday, hours in days.items():
            weeks[isoday[1]] += hours
        return weeks


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry
        for contract, contract_work_entries in work_entries_by_contract.items():
            if contract.work_entry_source != 'calendar':
                continue
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - contract_work_entries._to_intervals()

    def compute_sheet(self):
        self.ensure_one()
        if not self.employee_ids:
            return {'type': 'ir.actions.act_window_close'}
        payslip_run = self.env['hr.payslip.run']
        if self.env.context.get('active_id'):
            payslip_run = payslip_run.browse(self.env.context.get('active_id'))
        if not payslip_run:
            payslip_run = payslip_run.create({'name': _('Payslip Batch'), 'date_start': self.date_start, 'date_end': self.date_end})
        employees = self.employee_ids
        contracts = employees._get_contracts(self.date_start, self.date_end, states=['open', 'close'])
        if not contracts:
            raise UserError(_('No active or recently closed contracts found for the selected employees.'))
        work_entries = self.env['hr.work.entry'].search([('contract_id', 'in', contracts.ids), ('date_start', '<=', self.date_end), ('date_stop', '>=', self.date_start)])
        self._check_undefined_slots(work_entries, payslip_run)
        work_entries._check_if_error()
        payslips_vals = []
        for contract in contracts:
            payslips_vals.append({
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': self.date_start,
                'date_to': self.date_end,
                'contract_id': contract.id,
                'struct_id': contract.structure_type_id.default_struct_id.id or contract.struct_id.id,
            })
        payslips = self.env['hr.payslip'].create(payslips_vals)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window', 'res_model': 'hr.payslip.run', 'view_mode': 'form', 'res_id': payslip_run.id, 'target': 'current'}
