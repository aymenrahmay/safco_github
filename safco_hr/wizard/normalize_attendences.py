# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging


from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class NormalizeAttendences(models.TransientModel):
    _name = 'normalize.attendences'
    _description = 'normalize.attendences'

    @api.model
    def action_normalize_attendences_wizard(self):
        portal_wizard = self.create({})
        return portal_wizard._action_open_modal()

    def _action_open_modal(self):
        """Allow to keep the wizard modal open after executing the action."""
        return {
            'name': _('Normalize attendences'),
            'type': 'ir.actions.act_window',
            'res_model': 'normalize.attendences',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_normalize_attendences(self):
        attendance_ids = self.env.context.get('active_ids', [])
        selected_attendance_ids = self.env['hr.attendance'].sudo().browse(attendance_ids)
        for attendance in selected_attendance_ids:
            normalized_date_from,normalized_date_to = self.get_hour_to_from(attendance.employee_id,attendance.check_in)
            work_hour_entry_id = self.env['hr.work.entry'].search([('attendance_id', '=', attendance.id)], limit=1)
            attendance.sudo().write({'check_in': normalized_date_from, 'check_out': normalized_date_to, 'is_normalized': True})
            work_hour_entry_id.sudo().write({'date_start': normalized_date_from, 'date_stop': normalized_date_to})

        return True

    def get_hour_to_from(self,employee_id,date):
        resource_calendar_id = employee_id.resource_calendar_id
        day_num = date.weekday()
        hour_from = self.env['resource.calendar.attendance'].search([('dayofweek', '=', day_num), ('calendar_id', '=', resource_calendar_id.id)],
                                                                    limit=1).hour_from
        hour_to = self.env['resource.calendar.attendance'].search([('dayofweek', '=', day_num), ('calendar_id', '=', resource_calendar_id.id)], limit=1).hour_to
        normalized_date_from= date.replace(hour=int(hour_from)-3, minute=0, second=0)
        normalized_date_to= date.replace(hour=int(hour_to)-3, minute=0, second=0)
        return normalized_date_from,normalized_date_to