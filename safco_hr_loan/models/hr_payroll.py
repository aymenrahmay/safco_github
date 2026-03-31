
from odoo import api, fields, models


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string='Loan Installment')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model_create_multi
    def create(self, vals_list):
        payslips = super().create(vals_list)
        for payslip in payslips:
            payslip._compute_input_line_ids()
        return payslips

    def get_sum_lo_lines(self, payslip):
        lo_sum = 0
        for line in payslip.input_line_ids:
            if line.input_type_id.code == 'Loan':
                lo_sum += line.amount
        return lo_sum

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids() or []
        for slip in self:
            loan_inputs = slip.get_inputs()
            if loan_inputs:
                existing_loan_lines = slip.input_line_ids.filtered(lambda l: l.loan_line_id)
                if existing_loan_lines:
                    slip.input_line_ids = [(3, line.id) for line in existing_loan_lines]
                slip.write({'input_line_ids': [(0, 0, line) for line in loan_inputs]})
        return res

    def get_inputs(self):
        self.ensure_one()
        loans = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'paid')])
        loan_inputs = []
        for loan in loans:
            for loan_line in loan.loan_lines.filtered(lambda line: self.date_from <= line.date <= self.date_to and not line.paid):
                loan_inputs.append({
                    'contract_id': self.contract_id.id,
                    'name': 'Loan of : %s , amount %s From : %s' % (loan.employee_id.name, loan_line.amount, loan.name),
                    'amount': loan_line.amount,
                    'input_type_id': self.env.ref('safco_hr_loan.input_loan').id,
                    'loan_line_id': loan_line.id,
                })
        return loan_inputs

    def action_payslip_done(self):
        for payslip in self:
            for line in payslip.input_line_ids:
                if line.loan_line_id:
                    line.loan_line_id.paid = True
                    line.loan_line_id.loan_id._compute_loan_amount()
        return super().action_payslip_done()
