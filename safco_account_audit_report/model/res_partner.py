# -*- coding: utf-8 -*-
from odoo import api, fields, models
from num2words import num2words

class ResPartner(models.Model):
    _inherit = 'res.partner'

    audit_report_id = fields.Binary( string="Audit report", attachment=True)
    to_print_on_audit_report_balance = fields.Char(readonly=True, string="Audit report value")
    #to_print_on_audit_report_balance_ar_char = fields.Char(readonly=True, string="Text value to be printed")


