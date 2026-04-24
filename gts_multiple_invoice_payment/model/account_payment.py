from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'
    _description = 'Payment Invoice Line'

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
        string="Payment Status", related='invoice_id.payment_state',
        store=True)
    select = fields.Boolean('Select', help="Click to select the invoice")

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise UserError(_('Amount to pay can not be less than 0! (Invoice code: %s)')
                                % line.invoice_id.name)
            if line.amount > line.residual:
                raise UserError(_('"Amount to pay" can not be greater than than "Amount '
                                  'Due" ! (Invoice code: %s)')
                                % line.invoice_id.name)

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            self.amount_total = self.invoice_id.amount_total
            self.residual = self.invoice_id.amount_residual
        else:
            self.amount_total = 0.0
            self.residual = 0.0

    @api.onchange('select')
    def onchange_select(self):
        if self.select:
            self.amount = self.invoice_id.amount_residual
        else:
            self.amount = 0.0


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_total = fields.Float('Invoice Total',
                                 help="Shows total invoice amount selected for this payment")
    invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', 'Selected Invoices',
                                    help='Please select invoices for this partner for the payment')
    selected_inv_total = fields.Float(compute='compute_selected_invoice_total',
                                      store=True, string='Assigned Amount')
    balance = fields.Float(compute='_compute_balance', string='Balance')

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def _compute_balance(self):
        for payment in self:
            total = sum(payment.invoice_lines.mapped('amount'))
            payment.balance = payment.amount - total

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def compute_selected_invoice_total(self):
        for payment in self:
            payment.selected_inv_total = sum(payment.invoice_lines.mapped('amount'))

    @api.onchange('partner_id', 'payment_type','amount')
    def onchange_partner_id(self):
        Invoice = self.env['account.move']
        if self.partner_id:
            partners_list = self.partner_id.child_ids.ids
            partners_list.append(self.partner_id.id)
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
            line_vals = [fields.Command.clear()]
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
                line_vals.append(fields.Command.create(data))
            self.invoice_lines = line_vals
        else:
            self.invoice_lines = [fields.Command.clear()]

    @api.onchange('invoice_lines')
    def onchange_invoice_lines(self):
        if self.invoice_lines:
            self.invoice_total = sum(self.invoice_lines.mapped('amount'))
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
            total = sum(payment.invoice_lines.mapped('amount'))
            if payment.invoice_lines:
                if round(total,2) > round(payment.amount,2):
                    raise UserError(_('You cannot select more value invoices than the payment amount. '
                                      'Total: {} Payment Amount: {}').format(total, payment.amount))

    def action_post(self):
        payments_to_reconcile = self.filtered(lambda payment: any(payment.invoice_lines.mapped('amount')))
        for payment in payments_to_reconcile.filtered(lambda payment: not payment.outstanding_account_id):
            payment.outstanding_account_id = payment._get_outstanding_account(payment.payment_type).id

        res = super(AccountPayment, self).action_post()
        for payment in self:
            if payment.account_manager and 'invoice_user_id' in payment.move_id._fields:
                payment.move_id.invoice_user_id = payment.account_manager.id
            if payment in payments_to_reconcile:
                if not payment.move_id:
                    payment._generate_journal_entry()
                if payment.move_id.state == 'draft':
                    payment.move_id.action_post()
                payment._reconcile_selected_invoice_lines()
        return res

    def _prepare_move_lines_per_type(self, write_off_line_vals=None, force_balance=None):
        line_vals_per_type = super()._prepare_move_lines_per_type(
            write_off_line_vals=write_off_line_vals,
            force_balance=force_balance,
        )
        invoice_lines = self.invoice_lines.filtered(lambda line: line.amount > 0 and line.invoice_id)
        if not invoice_lines:
            return line_vals_per_type

        counterpart_lines = line_vals_per_type.get('counterpart_lines') or []
        if len(counterpart_lines) != 1:
            return line_vals_per_type

        counterpart_line = counterpart_lines[0]
        total_amount_currency = counterpart_line['amount_currency']
        total_balance = counterpart_line['balance']
        sign = -1 if total_amount_currency < 0 else 1
        split_lines = []

        allocated_amount_currency = 0.0
        allocated_balance = 0.0
        for invoice_line in invoice_lines:
            amount_currency = sign * abs(invoice_line.amount)
            balance = self.currency_id._convert(
                amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
            allocated_amount_currency += amount_currency
            allocated_balance += balance

            vals = dict(counterpart_line)
            vals.update({
                'amount_currency': amount_currency,
                'balance': balance,
            })
            split_lines.append(vals)

        remaining_amount_currency = total_amount_currency - allocated_amount_currency
        remaining_balance = total_balance - allocated_balance
        if (
            not self.currency_id.is_zero(remaining_amount_currency)
            or not self.company_id.currency_id.is_zero(remaining_balance)
        ):
            vals = dict(counterpart_line)
            vals.update({
                'amount_currency': remaining_amount_currency,
                'balance': remaining_balance,
            })

            split_lines.append(vals)

        line_vals_per_type['counterpart_lines'] = split_lines
        return line_vals_per_type

    def _reconcile_selected_invoice_lines(self):
        PartialReconcile = self.env['account.partial.reconcile']
        invoices_to_recompute = self.env['account.move']
        for payment in self:
            for rec in payment.invoice_lines.filtered(lambda line: line.amount > 0):
                invoice_line = rec.invoice_id.line_ids.filtered(
                    lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
                    and not line.reconciled
                )[:1]
                payment_line = payment._get_payment_line_to_reconcile(rec, invoice_line)
                if not invoice_line:
                    raise UserError(_(
                        "Could not find an open receivable/payable line on invoice %s."
                    ) % rec.invoice_id.display_name)
                if not payment_line:
                    payment_accounts = ', '.join(payment.move_id.line_ids.mapped('account_id.display_name')) or _('No journal items found')
                    raise UserError(_(
                        "Could not find a payment receivable/payable line to reconcile invoice %(invoice)s.\n"
                        "Invoice account: %(invoice_account)s\n"
                        "Payment journal entry accounts: %(payment_accounts)s"
                    ) % {
                        'invoice': rec.invoice_id.display_name,
                        'invoice_account': invoice_line.account_id.display_name,
                        'payment_accounts': payment_accounts,
                    })
                if payment_line.account_id != invoice_line.account_id:
                    raise UserError(_(
                        "The payment line account does not match invoice %(invoice)s.\n"
                        "Invoice account: %(invoice_account)s\n"
                        "Payment account: %(payment_account)s"
                    ) % {
                        'invoice': rec.invoice_id.display_name,
                        'invoice_account': invoice_line.account_id.display_name,
                        'payment_account': payment_line.account_id.display_name,
                    })

                debit_line = invoice_line if invoice_line.balance > 0 else payment_line
                credit_line = payment_line if debit_line == invoice_line else invoice_line
                amount = payment.currency_id._convert(
                    abs(rec.amount),
                    payment.company_id.currency_id,
                    payment.company_id,
                    payment.date,
                )
                amount = min(amount, abs(debit_line.amount_residual), abs(credit_line.amount_residual))
                if payment.company_id.currency_id.is_zero(amount):
                    continue

                company_currency = payment.company_id.currency_id
                PartialReconcile.create({
                    'amount': amount,
                    'debit_amount_currency': abs(company_currency._convert(
                        amount,
                        debit_line.currency_id,
                        payment.company_id,
                        payment.date,
                    )),
                    'credit_amount_currency': abs(company_currency._convert(
                        amount,
                        credit_line.currency_id,
                        payment.company_id,
                        payment.date,
                    )),
                    'debit_move_id': debit_line.id,
                    'credit_move_id': credit_line.id,
                })
                invoices_to_recompute |= rec.invoice_id

        if invoices_to_recompute:
            self.env.add_to_compute(invoices_to_recompute._fields['payment_state'], invoices_to_recompute)
            self.env.add_to_compute(invoices_to_recompute._fields['amount_residual'], invoices_to_recompute)

    def _get_payment_line_to_reconcile(self, invoice_payment_line, invoice_line):
        if not invoice_line:
            return self.env['account.move.line']

        _liquidity_lines, counterpart_lines, _writeoff_lines = self._seek_for_lines()
        candidates = counterpart_lines.filtered(lambda line: not line.reconciled)
        if not candidates:
            return candidates

        same_account_candidates = candidates.filtered(lambda line: line.account_id == invoice_line.account_id)
        if same_account_candidates:
            candidates = same_account_candidates

        expected_amount = self.currency_id._convert(
            abs(invoice_payment_line.amount),
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        for line in candidates:
            if self.company_id.currency_id.compare_amounts(abs(line.balance), expected_amount) == 0:
                return line
        return candidates[:1]

    def copy(self, default=None):
        default = dict(default or {})
        default.update(invoice_lines=[], invoice_total=0.0)
        return super(AccountPayment, self).copy(default)
