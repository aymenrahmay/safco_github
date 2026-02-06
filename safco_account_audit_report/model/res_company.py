# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    safco_auditing_partner_id = fields.Many2one('res.partner', 'Auditing partner')
