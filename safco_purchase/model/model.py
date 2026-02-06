# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    user_id = fields.Many2one('res.users', string='purchase representative')

    @api.model
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id and self.partner_id.user_id:
            self.user_id = self.partner_id.user_id
        else:
            self.user_id= self.env.user
        return res

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    @api.model
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.partner_id.user_id:
            self.user_id = self.partner_id.user_id
        else:
            self.user_id= self.env.user
        return res