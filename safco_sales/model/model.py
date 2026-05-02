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
                    'price_unit': 0,
                    'product_uom_qty': res.product_uom_qty,
                    'product_uom': accessory_product_id.uom_id.id,
                })
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_cost = fields.Float('Order cost', readonly=True, compute='_compute_sale_order_cost')
    state = fields.Selection(
        selection_add=[('waiting_gm', 'Waiting GM Approval')],
        ondelete={'waiting_gm': 'set default'},
    )
    gm_approved_by = fields.Many2one('res.users', string='GM Approved By', readonly=True, copy=False)
    gm_approved_on = fields.Datetime(string='GM Approved On', readonly=True, copy=False)

    @api.depends('order_line.product_uom_qty', 'order_line.product_id.standard_price')
    def _compute_sale_order_cost(self):
        for order in self:
            order.sale_order_cost = sum(
                line.product_uom_qty * line.product_id.standard_price
                for line in order.order_line
            )

    def action_request_gm_approval(self):
        invalid_orders = self.filtered(lambda order: order.state not in ('draft', 'sent'))
        if invalid_orders:
            raise UserError(_('Only draft or sent quotations can be sent for GM approval.'))

        self.write({
            'state': 'waiting_gm',
            'gm_approved_by': False,
            'gm_approved_on': False,
        })

        for order in self:
            order.message_post(body=_('Sent for GM approval by %s') % self.env.user.partner_id.name)
        return True

    def gm_action_confirm(self):
        if not self.env.user.user_has_groups('sales_team.group_sale_manager'):
            raise UserError(_('Only a Sales Manager can confirm quotations.'))

        invalid_orders = self.filtered(lambda order: order.state != 'waiting_gm')
        if invalid_orders:
            raise UserError(_('Only quotations waiting for GM approval can be confirmed.'))

        result = super(SaleOrder, self).action_confirm()
        approval_time = fields.Datetime.now()
        self.write({
            'gm_approved_by': self.env.user.id,
            'gm_approved_on': approval_time,
        })

        for order in self:
            order.message_post(body=_('Approved by %s on %s') % (self.env.user.partner_id.name, approval_time))
        return result

    def action_confirm(self):
        if self.env.user.user_has_groups('sales_team.group_sale_manager'):
            return super().action_confirm()
        raise UserError(_('Use "Send for GM Approval". Only the GM can confirm quotations.'))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        for partner in self:
            if vals.get('active') is False and partner.credit > 0:
                raise UserError(_('You can\'t archive partner when credit is bigger than zero (0).'))
        return super(ResPartner, self).write(vals)
