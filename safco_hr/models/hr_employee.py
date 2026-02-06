# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
from http.client import BadStatusLine
from logging import getLogger

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = getLogger(__name__)
GENDER_SELECTION = [('male', 'Male'), ('female', 'Female')]

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    personal_mobile = fields.Char(string='Mobile', related='address_home_id.mobile', store=True,
                                  help="Personal mobile number of the employee")
    joining_date = fields.Date(string='Joining Date',
                               help="Employee joining date computed from the contract start date",
                               compute='compute_joining', store=True)
    expiry_date = fields.Date(string='ID Expiry Date', help='Expiry date of Identification ID')
    passport_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Passport ID')
    id_attachment_id = fields.Many2many('ir.attachment', 'id_attachment_rel', 'id_ref', 'attach_ref',
                                        string="Attachment", help='You can attach the copy of your Id')
    passport_attachment_id = fields.Many2many('ir.attachment', 'passport_attachment_rel', 'passport_ref', 'attach_ref1',
                                              string="Attachment",
                                              help='You can attach the copy of Passport')
    fam_ids = fields.One2many('hr.employee.dependents', 'employee_id', string='Dependents',
                              help='Dependents Information')
    insurence_ids = fields.One2many('hr.employee.insurance', 'employee_id', string='Insurence')

    @api.depends('contract_id')
    def compute_joining(self):
        for emp in self:
            emp.joining_date = False
            if emp.contract_id:
                emp.joining_date = min(emp.contract_id.mapped('date_start'))

    def mail_reminder_check_all_documents(self):
        now = datetime.now() + timedelta(days=1)
        employee_ids = self.search([])


    def mail_reminder(self):
        """Documents expiry date notification"""
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        employee_ids = self.search([])


        for employee in employee_ids:
            if employee.expiry_date:
                exp_date = fields.Date.from_string(employee.expiry_date) - timedelta(days=30)
                if date_now >= exp_date:
                    body_html = "  Hello  ,<br> National ID of : " + employee.name +" is going to expire, Please renew it before expiry date"
                    subject = _('National ID of : %s  Expire On %s') % (employee.name, employee.expiry_date)
                    self.compose_and_send_mail(body_html, subject, employee)

            if employee.passport_expiry_date:
                exp_date1 = fields.Date.from_string(employee.passport_expiry_date) - timedelta(days=180)
                if date_now >= exp_date1:
                    body_html = "  Hello ,<br>Passport of: " + employee.name + " is going to expire, Please renew it before expiry date"
                    subject = _('Passport of : -%s is going to expire') % (employee.name)
                    self.compose_and_send_mail(body_html, subject, employee)

            if employee.insurence_ids:
                for insurence in employee.insurence_ids:
                    insurence_exp_date = fields.Date.from_string(insurence.end_date) - timedelta(days=30)
                    if date_now >= insurence_exp_date:
                        body_html = "Hello  ,<br>The " +insurence.insurance_type_id.name + "of :"+ employee.name+ " is going to expire, Please renew it before expiry date"
                        subject = _('Insurence-%s of-%s is going to expire') % (insurence.insurance_type_id.name, employee.name)
                        self.compose_and_send_mail(body_html, subject, employee)

    def compose_and_send_mail(self, body, subject, employee):
        message = self.env['mail.message'].create({
            'subject': subject,
            'body': body,
            'email_from': self.env.user.company_id.email,
            'reply_to': self.env.user.company_id.email,
            'model': 'hr.employee',
            'res_id': employee.id,

        })
        self.env['mail.mail'].with_context(wo_bounce_return_path=True).create({
            'mail_message_id': message.id,
            'body_html': body,
            'email_to': self.env['ir.config_parameter'].sudo().get_param('hr_resignation.email_expiries_manager'),
            'email_cc': employee.work_email,
        }).sudo().send()

    def compose_and_send_mail_2(self, body, subject):
        message = self.env['mail.message'].create({
            'subject': subject,
            'body': body,
            'email_from': self.env.user.company_id.email,
            'reply_to': self.env.user.company_id.email,
            'model': 'hr.employee',
            'res_id': 57,

        })
        self.env['mail.mail'].with_context(wo_bounce_return_path=True).create({
            'mail_message_id': message.id,
            'body_html': body,
            'email_to': self.env['ir.config_parameter'].sudo().get_param('hr_resignation.email_expiries_manager'),
        }).sudo().send()




class HrEmployeeDependentsInfo(models.Model):
    """employee dependents information"""

    _name = 'hr.employee.dependents'
    _description = 'HR Employee Dependents'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Relation", help="Relationship with the employee")
    member_name = fields.Char(string='Name')
    member_contact = fields.Char(string='Contact No')
    birth_date = fields.Date(string="Birth date", tracking=True)
    dependent_iqama_id = fields.Integer(string="National/Iqama ID")
    dependent_expiry_date = fields.Date(string='Expiry Date', help='Expiry date of Identification ID')


class EmployeeRelationInfo(models.Model):
    """employee dependents information"""

    _name = 'hr.employee.relation'

    name = fields.Char(string="Relationship", help="Relationship with thw employee")


class EmployeeInsuranceType(models.Model):
    _name = 'hr.employee.insurance.type'

    name = fields.Char(string="Insurance type")


class EmployeeInsurance(models.Model):
    _name = 'hr.employee.insurance'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    start_date = fields.Date(string="Start date", tracking=True)
    end_date = fields.Date(string="End date", tracking=True)
    insurance_type_id = fields.Many2one('hr.employee.insurance.type', string="Insurance type")
