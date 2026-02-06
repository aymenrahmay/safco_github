# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_qty = fields.Float('Quantity', default=1.0, digits=(16, 7), required=True)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    vise_number = fields.Char('Vessel number')
    total_qty = fields.Float('Total Qty',compute='compute_total_qty',store=True)
    total_mixing_time = fields.Char('Total mixing time')
    verified_by = fields.Char('Verified by')
    mixing_operator = fields.Char('Mixing operator')
    confirmation_date_time = fields.Datetime('Confirmation date time')
    remarks = fields.Char('Remarks')
    ph = fields.Char('PH')
    sp = fields.Char('Sp.Gravity')
    color = fields.Char('Color')
    od = fields.Char('ODour')
    gtavity = fields.Char('Refractive')
    other = fields.Char('Other')
    refractive = fields.Char('Refractive')
    status = fields.Selection('Status')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),], string='Status')


    @api.depends('move_raw_ids')
    def compute_total_qty(self):
        total=0
        for mrp in self:
            for line in mrp.move_raw_ids:
                total= total+line.product_uom_qty
            mrp.total_qty = total
