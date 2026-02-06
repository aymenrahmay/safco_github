# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin_sale_order_id = fields.Many2one('sale.order', string='Origin (Sale order)', compute='_get_sales_order')

    @api.depends('origin')
    def _get_sales_order(self):
        for picking in self:
            sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)] , limit=1)
            picking.origin_sale_order_id = sale_order_id.id
