
import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class NormalizeAttendences(models.TransientModel):
    _name = 'normalize.attendences'
    _description = 'normalize.attendences'

    @api.model
    def action_normalize_attendences_wizard(self):
        portal_wizard = self.create({})
        return portal_wizard._action_open_modal()

    def _action_open_modal(self):
        return {
            'name': _('Normalize attendences'),
            'type': 'ir.actions.act_window',
            'res_model': 'normalize.attendences',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_normalize_attendences(self):
        attendance_ids = self.env.context.get('active_ids', [])
        selected_attendance_ids = self.env['hr.attendance'].sudo().browse(attendance_ids)
        for attendance in selected_attendance_ids:
            normalized_date_from, normalized_date_to = self.get_hour_to_from(attendance.employee_id, attendance.check_in)
            work_hour_entry_id = self.env['hr.work.entry'].search([('attendance_id', '=', attendance.id)], limit=1)
            attendance.sudo().write({'check_in': normalized_date_from, 'check_out': normalized_date_to, 'is_normalized': True})
            if work_hour_entry_id:
                work_hour_entry_id.sudo().write({'date_start': normalized_date_from, 'date_stop': normalized_date_to})
        return {'type': 'ir.actions.act_window_close'}

    def get_hour_to_from(self, employee_id, date):
        resource_calendar_id = employee_id.resource_calendar_id
        day_num = str(date.weekday())
        attendance = self.env['resource.calendar.attendance'].search([('dayofweek', '=', day_num), ('calendar_id', '=', resource_calendar_id.id)], limit=1)
        hour_from = attendance.hour_from if attendance else 0.0
        hour_to = attendance.hour_to if attendance else 0.0
        normalized_date_from = date.replace(hour=max(int(hour_from) - 3, 0), minute=0, second=0)
        normalized_date_to = date.replace(hour=max(int(hour_to) - 3, 0), minute=0, second=0)
        return normalized_date_from, normalized_date_to
