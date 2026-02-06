# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_picking_update_effective_date(self,context=None):
        return {
                'name': ('UpdateEffectiveDate'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'update.effective.date',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new'
                }



