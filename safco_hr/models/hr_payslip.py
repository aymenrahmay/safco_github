
from collections import defaultdict

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import timedelta
from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    hr_payslip_run_total = fields.Float(compute='_compute_hr_payslip_run_total', string='Batch total')

    def _compute_hr_payslip_run_total(self):
        total_net= 0
        for run in self:
            for slip in run.slip_ids:
                total_net = total_net+ slip.net_wage
            run.hr_payslip_run_total = total_net


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    net_wage = fields.Float(compute='_compute_basic_net')
    requested_working_day = fields.Integer(compute='_compute_requested_working_days', store = True)


    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['account_id'] == account_id
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0))
            and (
                    (
                            not line_id['analytic_distribution'] and
                            not line.salary_rule_id.analytic_account_id.id and
                            not line.slip_id.contract_id.analytic_account_id.id
                    )
                    or (line_id['analytic_distribution'] and
                        (line.salary_rule_id.analytic_account_id.id in line_id['analytic_distribution'] or
                         line.slip_id.contract_id.analytic_account_id.id in line_id['analytic_distribution']))
            )
        )
        return next(existing_lines, False)

    def _compute_basic_net(self):
        for payslip in self:
            net_line = payslip.line_ids.filtered(lambda line: line.code == 'NET')
            payslip.net_wage = net_line.total

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_requested_working_days(self):
        for payslip in self:
            requested_working_day_based_on_dates = 0
            if payslip.date_from and payslip.date_to:
                date_from = fields.Date.from_string(payslip.date_from)
                date_to = fields.Date.from_string(payslip.date_to)
                # Initialize the counter for working days excluding Fridays
                working_day_count = 0
                # Use a while loop to iterate from date_from to date_to
                current_date = date_from
                while current_date <= date_to:
                    # Check if the current date is NOT a Friday (4 is the code for Friday)
                    if current_date.weekday() != 4:  # If not Friday
                        working_day_count += 1
                    else :
                        print ("Friday : "+str(current_date))
                    # Move to the next day
                    current_date += timedelta(days=1)

                # Assign the count of working days excluding Fridays
                requested_working_day_based_on_dates = working_day_count
            else:
                requested_working_day_based_on_dates = 0
            leave_type_records = self.env['hr.leave.type'].search([('time_type', '=', 'other')])
            # Extract the ids of the records found
            leave_type_ids = leave_type_records.ids
            leave_records = self.env['hr.leave'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', 'in', ['confirm', 'validate']),
                ('date_from', '>=', payslip.date_from),
                ('date_to', '<=', payslip.date_to),
                ('holiday_status_id', 'in', leave_type_ids)])
            total_number_of_days_display = sum(leave.number_of_days_display for leave in leave_records)
            ss =  requested_working_day_based_on_dates - int(total_number_of_days_display)
            payslip.requested_working_day = ss


    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_worked_days_line_ids(self):
        if not self or self.env.context.get('salary_simulation'):
            return
        valid_slips = self.filtered(
            lambda p: p.employee_id and p.date_from and p.date_to and p.contract_id and p.struct_id)
        # Make sure to reset invalid payslip's worked days line
        self.update({'worked_days_line_ids': [(5, 0, 0)]})
        # Ensure work entries are generated for all contracts
        generate_from = min(p.date_from for p in self)
        current_month_end = date_utils.end_of(fields.Date.today(), 'month')
        generate_to = max(min(fields.Date.to_date(p.date_to), current_month_end) for p in self)
        self.mapped('contract_id')._generate_work_entries(generate_from, generate_to)

        for slip in valid_slips:
            if not slip.struct_id.use_worked_day_lines:
                continue
            # YTI Note: We can't use a batched create here as the payslip may not exist
            slip.update({'worked_days_line_ids': slip._get_new_worked_days_lines()})

    def _attendance_fill_lines(self, lines, attendance_break_down):
        # Override to change comutation (e.g. grouping by week for overtime)
        # probably want to override _attendance_create_lines
        for isoday, worked_hours in attendance_break_down.items():
            lines['ATTN']['number_of_days'] += 1
            lines['ATTN']['number_of_hours'] += worked_hours

    def _attendance_create_lines(self, employee, contract, date_from, date_to):
        # Override to return more keys like this (e.g. OT Overtime)
        return {
            'ATTN': {
                'name': 'Attendance',
                'sequence': 10,
                'code': 'ATTN',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
        }

    def _attendance_domain(self, employee, contract, date_from, date_to):
        # Override if you need to limit by contract or similar.
        return [
            ('employee_id', '=', employee.id),
            ('check_in', '>=', date_from),
            ('check_in', '<=', date_to),
        ]

    def _attendance_get(self, employee, contract, date_from, date_to):
        # Override if you need to limit by contract or similar.
        return self.env['hr.attendance'].search(self._attendance_domain(employee, contract, date_from, date_to))

    def _attendance_hour_break_down(self, employee, contract, date_from, date_to):
        attns = self._attendance_get(employee, contract, date_from, date_to)
        day_values = defaultdict(float)
        for attn in attns:
            if not attn.check_out:
                raise ValidationError('This pay period must not have any open attendances.')
            if attn.worked_hours:
                # Avoid in/outs
                attn_iso = attn.check_in.isocalendar()
                day_values[attn_iso] += attn.worked_hours
        return day_values


    def hour_break_down(self, code):
        """
        :param code: what kind of worked days you need aggregated
        :return: dict: keys are isocalendar tuples, values are hours.
        """
        self.ensure_one()
        if code == 'ATTN':
            return self._attendance_hour_break_down(self.employee_id, self.contract_id, self.date_from, self.date_to)
        elif hasattr(super(HrPayslip, self), 'hour_break_down'):
            return super(HrPayslip, self).hour_break_down(code)

    def hours_break_down_week(self, code):
        """
        :param code: hat kind of worked days you need aggregated
        :return: dict: keys are isocalendar weeks, values are hours.
        """
        days = self.hour_break_down(code)
        weeks = defaultdict(float)
        for isoday, hours in days.items():
            weeks[isoday[1]] += hours
        return weeks

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            if contract.work_entry_source != 'calendar':
                continue
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            # if outside:
            #     time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in outside._items]])
            #     raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule. Time intervals to look for:%s") % (contract.employee_id.name, time_intervals_str))




    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        #Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
        if not employees:
            return success_result

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        date_start = datetime.combine(payslip_run.date_start, time.min)
        date_end = datetime.combine(payslip_run.date_end, time.max)

        #contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        contracts._generate_work_entries(date_start, date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if(self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            # if work_entries._check_if_error():
            #     work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
            #
            #     for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
            #         work_entries_by_contract[work_entry.contract_id] |= work_entry
            #
            #     for contract, work_entries in work_entries_by_contract.items():
            #         conflicts = work_entries._to_intervals()
            #         time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
            #     return {
            #         'type': 'ir.actions.client',
            #         'tag': 'display_notification',
            #         'params': {
            #             'title': _('Some work entries could not be validated.'),
            #             'message': _('Time intervals to look for:%s', time_intervals_str),
            #             'sticky': False,
            #         }
            #     }


        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslips_vals.append(values)
        payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return success_result
