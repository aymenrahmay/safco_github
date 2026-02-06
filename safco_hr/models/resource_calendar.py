

from odoo import fields, models, api

class ResourceCalendar(models.Model):
    _inherit = ['resource.calendar']

    penalty_sign_out = fields.Char('Penalty Sign out')
    penalty_sign_in = fields.Char('Penalty sign in')
