from odoo.exceptions import Warning
from odoo import models, fields, api, _


class HrEmployeeContract(models.Model):
    _inherit = 'hr.contract'

    paid_hourly_attendance = fields.Boolean(string="Paid Hourly Attendance", default=False)
    phone_allowance = fields.Float(help="Phone allowance.", default=0)
    housing_allowance = fields.Float(help="Housing allowance.", default=0)
    transportation_allowance = fields.Float(help="Transportation allowance.", default=0)
    default_struct_id = fields.Many2one('hr.payroll.structure', string="Regular Pay Structure", related="structure_type_id.default_struct_id")

    def _get_default_notice_days(self):
        if self.env['ir.config_parameter'].get_param('hr_resignation.notice_period'):
            return self.env['ir.config_parameter'].get_param('hr_resignation.no_of_days')
        else:
            return 0


    type_id = fields.Many2one('hr.contract.type', string="Contract type",
                              required=True, help="Contract type",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    notice_days = fields.Integer(string="Notice Period", default=_get_default_notice_days)
    name = fields.Char('Contract Reference',required=False, readonly=True,copy=False,default='/')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.ref')+":" + self.env['hr.employee'].browse(vals['employee_id']).name
        return super(HrEmployeeContract, self).create(vals)

