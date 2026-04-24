# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    partner_vat = fields.Char(string='Vat number', related='partner_id.vat')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.name = "***"


