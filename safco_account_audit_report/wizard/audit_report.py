# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, _
import base64
from datetime import timedelta, datetime
from num2words import num2words
import re

_logger = logging.getLogger(__name__)


class SendAnnualAuditReport(models.TransientModel):
    _name = 'audit.report'
    _description = 'Send annual audit report'

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    due_amount = fields.Char('Due amount to be included in the report')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    @api.model
    def default_get(self, fields):
        res = super(SendAnnualAuditReport, self).default_get(fields)
        current_year = datetime.now().year
        res['start_date'] = f'{current_year}-01-01'  # First day of the year
        res['end_date'] = f'{current_year}-12-31'  # Last day of the year
        if self.env.context.get('active_id'):
            res['partner_id'] = self.env.context['active_id']
        return res


    def _compute_due_amount(self):
        for record in self:
            report = self.env.ref('account_reports.partner_ledger_report')
            options = self._generate_options(report,self.partner_id.id, self.start_date,
                                             self.end_date)
            res = report._get_lines(options)
            customer_balances = {}
            for entry in res:
                if entry['id'] == 'total~~':
                    continue
                # Retrieve the last column's value which is the balance
                last_column = entry['columns'][-1]  # get the last column
                balance_name = last_column['name']
                balance_value = last_column['no_format']
                # Store in a dictionary with customer name as key
                customer_balances[entry['name']] = {
                    'formatted': balance_name,
                    'numeric': balance_value
                }

            # Output the results
            for customer, balance in customer_balances.items():
                return balance['formatted']
            return True

    def _generate_options(self, report, partner_id, date_from, date_to, default_options=None):
        if isinstance(date_from, datetime):
            date_from_str = fields.Date.to_string(date_from)
        else:
            date_from_str = date_from

        if isinstance(date_to, datetime):
            date_to_str = fields.Date.to_string(date_to)
        else:
            date_to_str = date_to

        if not default_options:
            default_options = {}

        return report._get_options({
            'report_id': report.id,
            'partner_ids': [partner_id],
            'date': {
                'date_from': date_from_str,
                'date_to': date_to_str,
                'mode': 'range',
                'filter': 'custom',
            },
            **default_options,
        })

    def action_print_audit_report(self):
        self.ensure_one()
        self._generate_pdf_audit_report()

    def _generate_pdf_audit_report(self):
        balance = self._compute_due_amount()
        clean_balance_number = re.sub(r'[^\d.,]', '', balance).replace(',', '')
        clean_balance_txt = num2words(float(clean_balance_number), lang='ar')
        self.partner_id.write({'to_print_on_audit_report_balance': '# '+clean_balance_number+' # ('+clean_balance_txt +')'})

        # Get the report
        report_template = self.env.ref('safco_account_audit_report.audit_report_report' )# Make sure this is correct
        if report_template:
            # Generate the PDF and attach it
            pdf = self.env['ir.actions.report']._render_qweb_pdf(report_template, self.partner_id.id)[0]
            pdf = base64.b64encode(pdf).decode()
            if pdf:
                attachments = self.env['ir.attachment'].search([
                    ('name', 'ilike', 'AuditReport%'),  # Name starts with 'audit'
                    ('res_model', '=', 'res.partner'),  # Object type is 'res.partner'
                    ('res_id', '=', self.partner_id.id)  # Link to the current partner
                ])
                attachments.unlink()
                self.partner_id.audit_report_id = pdf

                return True

        return False
