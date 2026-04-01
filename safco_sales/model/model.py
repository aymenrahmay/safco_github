# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.name = "***"

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.product_id.accessory_product_ids:
            for accessory_product_id in res.product_id.accessory_product_ids:
                self.env['sale.order.line'].create({
                    'order_id': res.order_id.id,
                    'product_id': accessory_product_id.id,
                    'name': '***',
                    'price_unit':0,
                    'product_uom_qty': res.product_uom_qty,
                    'product_uom':accessory_product_id.uom_id.id
                })
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_cost = fields.Float('Order cost', readonly=True, compute='_get_order_cost')
    approval_required = fields.Html("Approval Required", readonly=True, copy= False)
    need_gm_approval= fields.Boolean('Waiting for GM approval')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('waiting', 'waiting GM approval'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='draft')



    def gm_action_confirm(self):
        orders_to_approve = self.filtered(lambda order: order.state in ('draft', 'sent', 'waiting'))
        invalid_orders = self - orders_to_approve
        if invalid_orders:
            raise UserError(_('Only draft, sent, or waiting quotations can be approved by GM.'))

        orders_to_approve.filtered(lambda order: order.state == 'waiting').write({'state': 'sent'})
        result = super(SaleOrder, orders_to_approve).action_confirm()

        approval_message = "<span style='color:green;'>Order approved by: %s</span>" % self.env.user.partner_id.name
        orders_to_approve.write({'approval_required': approval_message})
        return result

    @api.depends('order_line')
    def _get_order_cost(self):
        total_cost = sum(line.product_uom_qty * line.product_id.standard_price for line in self.order_line)
        self.sale_order_cost = total_cost

    def action_confirm(self):
        for rec in self:
            if rec.user_id:
                selected_analytic_account_id = self.env['account.analytic.account'].search(
                    [('partner_id', '=', rec.user_id.partner_id.id)], limit =1)
                if selected_analytic_account_id:
                    for line in self.order_line:
                        line.write({'analytic_distribution': {selected_analytic_account_id.id: 100}})
            if rec.state == 'draft':
                approval_message = f"<span style='color:red;'>Second approval is needed for all quotes </span>"
                rec.write({ 'state': 'waiting', 'approval_required': approval_message,})

    def action_approve(self):
        if self.env.user.user_has_groups('sales_team.group_sale_manager'):
            return super().action_confirm()
        else:
            raise UserError(_('You can''t approve this order , only managers can approve'))

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        for partner in self:
            if vals.get('active') is False and  partner.credit >0:
                raise UserError(_('You can''t archive partner when credit is bigger than zero(0) '))
            else:
                return super(ResPartner, self).write(vals)

