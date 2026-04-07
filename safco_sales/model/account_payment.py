# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    num_chk = fields.Char(string='Check Number')
    bank = fields.Many2one('res.bank', string='Bank name')
    user_id = fields.Many2one('res.users', string='sales person',
                                       related='partner_id.user_id', readonly=True,
                                       help='related sales person to the contact', store= True )
    account_manager = fields.Many2one('res.users', string='Account manager',readonly=True,
                                      help='Account manager')
    move_name = fields.Char(string='Journal Entry Name', readonly=True,
                            related='move_id.name',
                            help="Technical field holding the number given to the journal entry, automatically set when the statement line is reconciled then stored to set the same number again if the line is cancelled, set to draft and re-processed again.")
    invoice_user_id = fields.Many2one('res.users', string='Salesperson', readonly=True,
                                      related='partner_id.user_id')

    def write(self, vals):
        if 'sequence_code' in vals:
            for approval_category in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if approval_category.sequence_id:
                    approval_category.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', approval_category.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    approval_category.sequence_id = sequence
        if 'company_id' in vals:
            for approval_category in self:
                if approval_category.sequence_id:
                    approval_category.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        payments = super().create(vals_list)

        for payment, vals in zip(payments, vals_list):
            if not vals.get('account_manager') and payment.partner_id and payment.partner_id.user_id:
                payment.account_manager = payment.partner_id.user_id.id

        return payments