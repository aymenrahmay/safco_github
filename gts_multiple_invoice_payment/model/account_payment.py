from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'

    invoice_id = fields.Many2one('account.move', 'Invoice')
    invoice_sales_person_id = fields.Many2one(related='invoice_id.user_id',
                                         string='Invoice sales person', store=True)
    payment_id = fields.Many2one('account.payment', 'Related Payment')
    account_manager_id = fields.Many2one(related='payment_id.account_manager',
                                         string='Account manager', store = True)
    payment_date = fields.Date(related='payment_id.date',
                                         string='Payment date', store=True)
    partner_id = fields.Many2one(related='invoice_id.partner_id',
                                 string='Partner', store = True)
    amount_total = fields.Float('Amount Total')
    residual = fields.Float('Amount Due')
    amount = fields.Float('Amount To Pay',
                          help="Enter amount to pay for this invoice, supports partial payment")
    invoice_date = fields.Date('Invoice Date')
    payment_state = fields.Selection(
        selection=lambda self: self.env["account.move"]._fields["payment_state"].selection,
        string="Payment Status", related='invoice_id.payment_state',
        store=True)
    select = fields.Boolean('Select', help="Click to select the invoice")

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise UserError(_('Amount to pay can not be less than 0! (Invoice code: %s)')
                                % line.invoice_id.number)
            if line.amount > line.residual:
                raise UserError(_('"Amount to pay" can not be greater than than "Amount '
                                  'Due" ! (Invoice code: %s)')
                                % line.invoice_id.number)

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            self.amount_total = self.invoice_id.amount_total
            self.residual = self.invoice_id.residual
        else:
            self.amount_total = 0.0
            self.residual = 0.0

    @api.onchange('select')
    def onchange_select(self):
        if self.select:
            self.amount = self.invoice_id.residual
        else:
            self.amount = 0.0


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_total = fields.Float('Invoice Total',
                                 help="Shows total invoice amount selected for this payment")
    invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', 'Invoices',
                                    help='Please select invoices for this partner for the payment')
    selected_inv_total = fields.Float(compute='compute_selected_invoice_total',
                                      store=True, string='Assigned Amount')
    balance = fields.Float(compute='_compute_balance', string='Balance')

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def _compute_balance(self):
        for payment in self:
            total = 0.0
            for line in payment.invoice_lines:
                total += line.amount
            if payment.amount >= total:
                balance = payment.amount - total
            else:
                balance = payment.amount - total
            payment.balance = balance

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def compute_selected_invoice_total(self):
        for payment in self:
            total = 0.0
            for line in payment.invoice_lines:
                total += line.amount
            payment.selected_inv_total = total

    @api.onchange('partner_id', 'payment_type','amount')
    def onchange_partner_id(self):
        Invoice = self.env['account.move']
        PaymentLine = self.env['payment.invoice.line']
        if self.partner_id:
            partners_list = self.partner_id.child_ids.ids
            partners_list.append(self.partner_id.id)
            line_ids = []
            move_type = ''
            if self.payment_type == 'outbound':
                move_type = 'in_invoice'
            elif self.payment_type == 'inbound':
                move_type = 'out_invoice'
            invoices = Invoice.search([('partner_id', 'in', partners_list),
                                       ('state', 'in', ('posted',)), ('move_type', '=', move_type),
                                       ('payment_state', '!=', 'paid')], order="invoice_date")

            total_amount = 0
            if self.amount > 0:
                total_amount = self.amount
            for invoice in invoices:
                assigned_amount = 0
                if total_amount > 0:
                    if invoice.amount_residual < total_amount:
                        assigned_amount = invoice.amount_residual
                        total_amount -= invoice.amount_residual
                    else:
                        assigned_amount = total_amount
                        total_amount = 0
                data = {
                    'invoice_id': invoice.id,
                    'amount_total': invoice.amount_total,
                    'residual': invoice.amount_residual,
                    'amount': assigned_amount,
                    'invoice_date': invoice.invoice_date,
                }
                line = PaymentLine.create(data)
                line_ids.append(line.id)
                # line_data.append((0, 0, data))
            self.invoice_lines = [(6, 0, line_ids)]
        else:
            if self.invoice_lines:
                for line in self.invoice_lines:
                    line.unlink()
            self.invoice_lines = []

    @api.onchange('invoice_lines')
    def onchange_invoice_lines(self):
        if self.invoice_lines:
            total = 0.0
            for line in self.invoice_lines:
                total += line.amount
            self.invoice_total = total
        else:
            self.invoice_total = 0.0
            self.amount = 0.0

    @api.onchange('amount')
    def onchange_amount(self):
        ''' Function to reset/select invoices on the basis of invoice date '''
        if self.amount > 0:
            total_amount = self.amount
            for line in self.invoice_lines:
                if total_amount > 0:
                    if line.residual < total_amount:
                        line.amount = line.residual
                        total_amount -= line.residual
                    else:
                        line.amount = total_amount
                        total_amount = 0
        if (self.amount <= 0):
            for line in self.invoice_lines:
                line.amount = 0.0

    @api.constrains('amount', 'invoice_lines')
    def _check_invoice_amount(self):
        ''' Function to validate if user has selected more amount invoices than payment '''
        for payment in self:
            total = 0.0
            if payment.invoice_lines:
                for line in payment.invoice_lines:
                    total += line.amount
                if round(total,2) > round(payment.amount,2):
                    raise UserError(_('You cannot select more value invoices than the payment amount. '
                                      'Total: {} Payment Amount: {}').format(total, payment.amount))

    

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        self.move_id.invoice_user_id = self.account_manager.id
        credit_move_id = self.move_id.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable','liability_payable'))

        for rec in self.invoice_lines:
            if rec.amount > 0:
                debit_move_id = rec.invoice_id.line_ids.filtered(
                    lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
                amount = abs(rec.amount)
                if self.payment_type == 'outbound':
                    amount = -abs(rec.amount)
                inv_obj = {
                    'amount': amount,
                    'debit_amount_currency': amount,
                    'credit_amount_currency': amount,
                    'debit_move_id': debit_move_id.id,
                    'credit_move_id': credit_move_id.id,
                }
                reconcile = self.env['account.partial.reconcile'].create(inv_obj)
        return res


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(invoice_lines=[], invoice_total=0.0)
        return super(AccountPayment, self).copy(default)
