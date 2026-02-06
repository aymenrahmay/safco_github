# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from odoo.tools import float_round, date_utils, convert_file, html2plaintext, is_html_empty, format_amount


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model_create_multi
    def create(self, vals_list):
        payslips = super().create(vals_list)
        print (payslips)
        for payslip in payslips:
            payslip._compute_input_line_ids()
        return payslips



    def get_sum_lo_lines(self,payslip_id):
        lo_sum = 0
        if payslip_id.input_line_ids:
            for line in payslip_id.input_line_ids:
                if line.input_type_id.code == 'Loan':
                    lo_sum = lo_sum+ line.amount
        return lo_sum

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to', 'struct_id')
    def _compute_input_line_ids(self):
        res = super(HrPayslip, self)._compute_input_line_ids() or []
        self.input_line_ids.unlink()
        loan_inputs = self.get_inputs()
        if loan_inputs:
            self.write({
                'input_line_ids': [(0, 0, line) for line in loan_inputs],
            })
        return res



    def get_inputs(self):
        for slip in self:
            """Compute other inputs to the employee payslip."""
            loans = self.env['hr.loan'].search([('employee_id', '=', slip.employee_id.id), ('state', '=', 'paid')])
            loan_inputs = []
            for loan in loans:
                for loan_line in loan.loan_lines.filtered(
                        lambda line: slip.date_from <= line.date <= slip.date_to and not line.paid):
                    new_input = {
                        'contract_id': slip.contract_id.id,
                        'name': 'Loan of : '+loan.employee_id.name+" , amount  "+ str(loan_line.amount) +" From : "+loan.name,
                        'amount': loan_line.amount,
                        'input_type_id': slip.env.ref('safco_hr_loan.input_loan').id,
                        'loan_line_id': loan_line.id,
                        'code': 'LO',  # You may need to adjust this based on your requirements
                        # Add other key-value pairs as needed
                    }
                    loan_inputs.append(new_input)
            return loan_inputs

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
