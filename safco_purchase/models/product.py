from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Income Analytic Account',
        company_dependent=True,
    )
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Expense Analytic Account',
        company_dependent=True,
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Income Analytic Account',
        company_dependent=True,
    )
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Expense Analytic Account',
        company_dependent=True,
    )

    def _get_product_analytic_accounts(self):
        self.ensure_one()
        expense_account = self.expense_analytic_account_id or self.categ_id.expense_analytic_account_id
        income_account = self.income_analytic_account_id or self.categ_id.income_analytic_account_id
        return expense_account, income_account
