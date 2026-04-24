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

    personal_mobile = fields.Char(string='Mobile', store=True,
                                  help="Personal mobile number of the employee")
    joining_date = fields.Date(string='Joining Date',
                               help="Employee joining date computed from the contract start date", store=True)
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



class HrEmployeeDependentsInfo(models.Model):
    """employee dependents information"""

    _name = 'hr.employee.dependents'
    _description = 'HR Employee Dependents'

    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Relation", help="Relationship with the employee")
    member_name = fields.Char(string='Name')
    member_contact = fields.Char(string='Contact No')
    birth_date = fields.Date(string="Birth date")
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
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    insurance_type_id = fields.Many2one('hr.employee.insurance.type', string="Insurance type")
