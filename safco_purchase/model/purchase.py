# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


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
            self.user_id = self.env.user
        return res


    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if self.order_line:
                for line in self.order_line:
                    if line.product_id and not line.analytic_distribution:
                        expense_ana_accounts , income_ana_accounts= line.product_id.product_tmpl_id._get_product_analytic_accounts()
                        line.write({'analytic_distribution': {expense_ana_accounts.id: 100}})
        return res