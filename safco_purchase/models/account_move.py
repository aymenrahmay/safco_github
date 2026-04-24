from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        if 'user_id' in self._fields:
            if self.partner_id and self.partner_id.user_id:
                self.user_id = self.partner_id.user_id
            else:
                self.user_id = self.env.user
        return res
