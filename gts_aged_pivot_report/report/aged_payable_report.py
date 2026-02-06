# -*- coding: utf-8 -*-
# Copyright 2015-2017 Geo Technosoft

from odoo import api, fields, models, tools


class AgedPayableReport(models.Model):
    '''
    This is report view table to show Variance Report
    '''
    _name = 'aged.payable.report'
    _rec_name = 'account_move_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner', readonly=True
    )
    parent_id = fields.Many2one(
        'res.partner',
        string='Group Partner', readonly=True
    )
    part1 = fields.Float('0 - 30', readonly=True)
    part2 = fields.Float('30 - 60', readonly=True)
    part3 = fields.Float('60 - 90', readonly=True)
    part4 = fields.Float('90 - 120', readonly=True)
    part5 = fields.Float('120 - 150', readonly=True)
    part6 = fields.Float('150 - 180', readonly=True)
    part7 = fields.Float('180 - 210', readonly=True)
    older = fields.Float('210 & Above', readonly=True)
    total = fields.Float('Total', readonly=True)
    undue = fields.Float('Undue', readonly=True)
    part8 = fields.Float('0 - 180', readonly=True)
    part9 = fields.Float('180 & Above', readonly=True)
    part10 = fields.Float('1 Year & Above', readonly=True)
    part11 = fields.Float('1.5 Year & Above', readonly=True)
    part12 = fields.Float('2 Year & Above', readonly=True)
    part13 = fields.Float('2.5 Year & Above', readonly=True)
    part14 = fields.Float('3 Year & Above', readonly=True)
    part15 = fields.Float('3.5 Year & Above', readonly=True)
    part16 = fields.Float('4 Year & Above', readonly=True)
    part17 = fields.Float('120 & Above', readonly=True)
    part18 = fields.Float('150 & Above', readonly=True)
    part19 = fields.Float('0 - 150', readonly=True)
    part20 = fields.Float('60 & Above', readonly=True)
    part21 = fields.Float('90 & Above', readonly=True)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    account_move_line_id = fields.Many2one('account.move.line', string='Journal Item', readonly=True)
    rating = fields.Char(string='Rating', readonly=True)
    salesperson = fields.Many2one('res.users', string='Salesperson', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
