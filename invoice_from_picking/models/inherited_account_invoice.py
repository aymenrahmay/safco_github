# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Accountinvoice(models.Model):
    _inherit = 'account.move'

    picking_ids = fields.Many2many('stock.picking', string="Picking References")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id.id
            self.invoice_user_id = self.partner_id.user_id.id


class SaleReport(models.Model):
    _inherit = 'sale.report'

    delivery_status = fields.Selection([
        ('pending', 'Not Delivered'),
        ('partial', 'Partially Delivered'),
        ('full', 'Fully Delivered'),
    ], string='Delivery Status')

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['delivery_status'] = "s.delivery_status"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.delivery_status"""
        return res

