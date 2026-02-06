
from odoo import api,fields,models,_
class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    leave_refuse_reason = fields.Text(string = "Refuse Reason")
    manager_id = fields.Many2one('hr.employee', string="Manager", related='employee_id.parent_id',help="Relationship with the employee")

    def reason_wizard(self,context=None):
        return {
                'name': ('Refuse Reason'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'leave.refuse.reason',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new'
                }
