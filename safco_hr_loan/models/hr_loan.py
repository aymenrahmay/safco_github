
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Request'

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        ts_user_id = result.get('user_id') or self.env.context.get('user_id', self.env.user.id)
        result.setdefault('employee_id', self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id)
        return result

    def _compute_loan_amount(self):
        for loan in self:
            total_paid = sum(loan.loan_lines.filtered('paid').mapped('amount'))
            loan.total_amount = loan.loan_amount
            loan.balance_amount = loan.loan_amount - total_paid
            loan.total_paid_amount = total_paid

    type = fields.Selection([('loan', 'Loan'), ('deduction', 'Deductions')], string='Type', default='loan', tracking=True, copy=False)
    name = fields.Char(string='Loan Name', default='/', readonly=True)
    description = fields.Text(string='Description', default='/')
    date = fields.Date(string='Date', default=fields.Date.today, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', readonly=True, string='Department')
    installment = fields.Integer(string='No Of Installments', default=1)
    payment_date = fields.Date(string='Payment Start Date', required=True, default=fields.Date.today)
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string='Loan Line', index=True)
    emp_account_id = fields.Many2one('account.account', string='Loan Account')
    treasury_account_id = fields.Many2one('account.account', string='Treasury Account')
    account_move_id = fields.Many2one('account.move', string='Journal entry', copy=False)
    journal_id = fields.Many2one('account.journal', string='Journal')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related='employee_id.job_id', readonly=True, string='Job Position')
    loan_amount = fields.Float(string='Loan Amount', required=True)
    total_amount = fields.Float(string='Total Amount', readonly=True, store=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string='Balance Amount', store=True, compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string='Total Paid Amount', store=True, compute='_compute_loan_amount')
    state = fields.Selection([('draft', 'Draft'), ('waiting_approval_1', 'Submitted'), ('waiting_approval_2', 'Waiting Approval'), ('approve', 'Approved'), ('paid', 'Paid'), ('refuse', 'Refused'), ('cancel', 'Canceled')], string='State', default='draft', tracking=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            values['name'] = self.env['ir.sequence'].next_by_code('hr.loan.seq') or '/'
        return super().create(vals_list)

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        return self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_approve(self):
        for loan in self:
            contract_obj = self.env['hr.contract'].search([('employee_id', '=', loan.employee_id.id), ('state', 'in', ['open', 'close'])], limit=1)
            if not contract_obj:
                raise UserError(_('You must define a contract for the employee.'))
            if not loan.loan_lines:
                raise ValidationError(_('Please compute the installment lines first.'))
        return self.write({'state': 'approve'})

    def post_loan(self):
        for loan in self:
            if loan.account_move_id:
                raise UserError(_('Account move is already created.'))
            amount = loan.loan_amount
            partner = loan.employee_id.user_id.partner_id if loan.employee_id.user_id else False
            if not loan.journal_id or not loan.emp_account_id or not loan.treasury_account_id:
                raise UserError(_('Please make sure that you set the journal, debit account and credit account.'))
            move = self.env['account.move'].create({
                'narration': loan.employee_id.name,
                'ref': loan.name,
                'journal_id': loan.journal_id.id,
                'date': loan.date,
                'line_ids': [
                    (0, 0, {'name': loan.employee_id.name, 'account_id': loan.emp_account_id.id, 'date': loan.date, 'partner_id': partner.id if partner else False, 'debit': amount if amount > 0.0 else 0.0, 'credit': -amount if amount < 0.0 else 0.0}),
                    (0, 0, {'name': loan.employee_id.name, 'account_id': loan.treasury_account_id.id, 'date': loan.date, 'partner_id': partner.id if partner else False, 'debit': -amount if amount < 0.0 else 0.0, 'credit': amount if amount > 0.0 else 0.0}),
                ],
            })
            if hasattr(move, 'action_post'):
                move.action_post()
            loan.write({'account_move_id': move.id, 'state': 'paid'})
        return True

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete a loan which is not in draft or cancelled state.'))
        return super().unlink()

    def compute_installment(self):
        for loan in self:
            loan.loan_lines.unlink()
            date_start = fields.Date.to_date(loan.payment_date)
            amount = loan.loan_amount / loan.installment if loan.installment else 0.0
            for _i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({'date': date_start, 'amount': amount, 'employee_id': loan.employee_id.id, 'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True


class InstallmentLine(models.Model):
    _name = 'hr.loan.line'
    _description = 'Installment Line'

    date = fields.Date(string='Payment Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Float(string='Amount', required=True)
    paid = fields.Boolean(string='Paid')
    loan_id = fields.Many2one('hr.loan', string='Loan Ref.')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip Ref.')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_employee_loans(self):
        for employee in self:
            employee.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', employee.id)])

    loan_count = fields.Integer(string='Loan Count', compute='_compute_employee_loans')
