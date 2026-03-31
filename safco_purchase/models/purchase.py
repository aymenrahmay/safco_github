from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    user_id = fields.Many2one('res.users', string='purchase representative')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id and self.partner_id.user_id:
            self.user_id = self.partner_id.user_id
        else:
            self.user_id = self.env.user
        return res

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            for line in order.order_line.filtered(lambda l: l.product_id and not l.analytic_distribution):
                expense_account, _income_account = line.product_id.product_tmpl_id._get_product_analytic_accounts()
                if expense_account:
                    line.analytic_distribution = {expense_account.id: 100}
        return res
