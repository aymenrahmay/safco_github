# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
            result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result


    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    type = fields.Selection([
        ('loan', 'Loan'),('deduction', 'Deductions'),], string="Type", default='loan', track_visibility='onchange', copy=False, )
    name = fields.Char(string="Loan Name", default="/", readonly=True)
    description = fields.Text(string="Description", default="/")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department")
    installment = fields.Integer(string="No Of Installments", default=1)
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today())
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    emp_account_id = fields.Many2one('account.account', string="Loan Account")
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    account_move_id = fields.Many2one('account.move', string="Jorunal entry", copy=False)
    journal_id = fields.Many2one('account.journal', string="Journal")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
    loan_amount = fields.Float(string="Loan Amount", required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, store=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", store=True, compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True, compute='_compute_loan_amount')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        res = super(HrLoan, self).create(values)
        return res

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            contract_obj = self.env['hr.contract'].search([('employee_id', '=', data.employee_id.id),
                                                           ('state', '=', 'open')], limit=1)
            if not contract_obj:
                raise UserError(_('You must Define a contract for employee.'))
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})
    #@api.multi
    def post_loan(self):
        for loan in self:
            if not loan.account_move_id:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.emp_account_id.id
                credit_account_id = loan.treasury_account_id.id
                if not journal_id or not debit_account_id or not credit_account_id:
                    raise UserError('Please make sure that you set the Journal and debit with the credit accounts')
                debit_vals = {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'partner_id': loan.employee_id.user_id.partner_id.id,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'loan_id': loan.id,
                }
                credit_vals = {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'partner_id': loan.employee_id.user_id.partner_id.id,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'loan_id': loan.id,
                }
                vals = {
                    'name': 'Loan For' + ' ' + loan_name,
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                self.write({'account_move_id': move.id, 'state': 'paid'})
                #move.post()
            else:
                raise UserError('Account move is already created')
        return True


    def post_loan(self):
        for loan in self:
            if not loan.account_move_id:
                amount = loan.loan_amount
                loan_name = loan.employee_id.name
                reference = loan.name
                journal_id = loan.journal_id.id
                debit_account_id = loan.emp_account_id.id
                credit_account_id = loan.treasury_account_id.id
                if not journal_id or not debit_account_id or not credit_account_id:
                    raise UserError('Please make sure that you set the Journal and debit with the credit accounts')
                debit_vals = {
                    'name': loan_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'partner_id': loan.employee_id.user_id.partner_id.id,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    #'loan_id': loan.id,
                }
                credit_vals = {
                    'name': loan_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'partner_id': loan.employee_id.user_id.partner_id.id,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    #'loan_id': loan.id,
                }
                vals = {
                    'narration': loan_name,
                    'ref': reference,
                    'journal_id': journal_id,
                    'date': loan.date,
                    'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                }
                move = self.env['account.move'].create(vals)
                self.write({'account_move_id': move.id, 'state': 'paid'})
                #move.post()
            else:
                raise UserError('Account move is already created')
        return True


    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()


    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')