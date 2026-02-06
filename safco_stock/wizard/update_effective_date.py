# -*- coding: utf-8 -*-
from odoo import api,fields,models,_

class UpdateEffectiveDate(models.TransientModel):
    _name = "update.effective.date"

    to_apply_date = fields.Date(string = "Date to apply", required = True)

    def update_effective_date(self):
        if self.env.context.get('active_model') == 'stock.picking':
            active_model_id = self.env.context.get('active_id')
            picking_id = self.env['stock.picking'].search([('id', '=', active_model_id)])
            if picking_id:
                picking_id.write({'date_done': self.to_apply_date})
                for move in picking_id.move_ids_without_package:
                    move.write({'date': self.to_apply_date})
