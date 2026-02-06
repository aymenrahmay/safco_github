from odoo import api, models, fields, _
from odoo.exceptions import UserError

import xlsxwriter
import base64
import datetime
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


class BankReportWiz(models.TransientModel):
    _name = 'bank.report.wiz'

    to_date = fields.Date('To Date', default=fields.Date.context_today, required=True)

    def open_bank_report_table(self):
        f_name = '/tmp/bank_report.xlsx'
        workbook = xlsxwriter.Workbook(f_name)
        worksheet = workbook.add_worksheet('Bank Report')
        worksheet.set_column('A:F', 6)
        date_format = workbook.add_format({'num_format': 'd-mmm-yyyy',
                                           'align': 'center'})
        bold_size_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        bold_size_format.set_font_size(12)
        align_value = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'})
        worksheet.write(4, 0, 'Invoice Date', bold_size_format)
        worksheet.write(4, 1, 'Invoice No.', bold_size_format)
        worksheet.write(4, 2, 'Party  Name', bold_size_format)
        worksheet.write(4, 3, '0-150', bold_size_format)
        worksheet.write(4, 4, '150 & Above', bold_size_format)
        worksheet.write(4, 5, '0-180', bold_size_format)
        worksheet.write(4, 6, '180 & Above', bold_size_format)
        worksheet.write(4, 7, 'Total Amount.', bold_size_format)

        date_format = '%Y-%m-%d'

        to_day_ = datetime.strptime(self.to_date, date_format)
        day_0 = to_day_.date()
        day_30 = to_day_.date() - timedelta(days=30)
        day_30_1 = day_30 - timedelta(days=1)
        day_60 = day_30_1 - timedelta(days=30)
        day_60_1 = day_60 - timedelta(days=1)
        day_90 = day_60_1 - timedelta(days=30)
        day_90_1 = day_90 - timedelta(days=1)
        day_120 = day_90_1 - timedelta(days=30)
        day_120_1 = day_120 - timedelta(days=1)
        day_150 = day_120_1 - timedelta(days=30)
        day_150_1 = day_150 - timedelta(days=1)
        day_180 = day_150_1 - timedelta(days=30)
        day_180_1 = day_180 - timedelta(days=1)
        day_210 = day_180_1 - timedelta(days=30)
        year_1 = day_0 - relativedelta(years=1)
        year_1_5 = year_1 - relativedelta(months=6)
        year_2 = year_1_5 - relativedelta(months=6)
        year_2_5 = year_2 - relativedelta(months=6)
        year_3 = year_2_5 - relativedelta(months=6)
        year_3_5 = year_3 - relativedelta(months=6)
        year_4 = year_3_5 - relativedelta(months=6)
        receivable_type = self.env['account.account.type'].search(
            [('name', '=', 'Receivable')], limit=1)
        if not receivable_type:
            raise UserError(_('Please configure "Receivable" account type!'))
        self._cr.execute("""
            select sum(balance), partner_id from account_move_line
            where partner_id is not null
            and user_type_id = %s
            and date <= '%s'
            group by partner_id""" % (receivable_type.id, day_0))
        result_partner = self._cr.fetchall()
        partners = []
        for data in result_partner:
            if data[0] == 0.0:
                partners.append(data[1])
        self._cr.execute(
            """
            with period1 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   sum(al.amount_residual) as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period2 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   sum(al.amount_residual) as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period3 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   sum(al.amount_residual) as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period4 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   sum(al.amount_residual) as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period5 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   sum(al.amount_residual) as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period6 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   sum(al.amount_residual) as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period7 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   sum(al.amount_residual) as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period8 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   sum(al.amount_residual) as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period9 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   sum(al.amount_residual) as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            older as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   sum(al.amount_residual) as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            undue_amount as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   sum(al.amount_residual) as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity > '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period10 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   sum(al.amount_residual) as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period11 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   sum(al.amount_residual) as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period12 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   sum(al.amount_residual) as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period13 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   sum(al.amount_residual) as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period14 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   sum(al.amount_residual) as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period15 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   sum(al.amount_residual) as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period16 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   sum(al.amount_residual) as part16,
                   0.0 as part17,
                   0.0 as part18,
                   0.0 as part19
                   from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period17 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   sum(al.amount_residual) as part17,
                   0.0 as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period18 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   sum(al.amount_residual) as part18,
                   0.0 as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity < '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            period19 as (
                select
                   al.id as account_move_line_id,
                   am.id as account_move_id,
                   al.partner_id as partner_id,
                   rp.parent_id as parent_id,
                   rp.user_id as salesperson,
                   al.move_id as invoice_id,
                   0.0 as part1,
                   0.0 as part2,
                   0.0 as part3,
                   0.0 as part4,
                   0.0 as part5,
                   0.0 as part6,
                   0.0 as part7,
                   0.0 as part8,
                   0.0 as part9,
                   0.0 as older,
                   0.0 as total,
                   0.0 as undue,
                   ai.invoice_date as date_inv,
                   0.0 as part10,
                   0.0 as part11,
                   0.0 as part12,
                   0.0 as part13,
                   0.0 as part14,
                   0.0 as part15,
                   0.0 as part16,
                   0.0 as part17,
                   0.0 as part18,
                   sum(al.amount_residual) as part19
                from account_move_line al
                join res_partner rp on rp.id = al.partner_id
                left join account_move am on am.id = al.move_id
                join account_move  ai on ai.id = al.move_id
                where rp.employee is FALSE
                and am.state = 'posted'
                and al.date_maturity between '%s' and '%s'
                and al.user_type_id = %s
                and al.amount_residual != 0.0
                group by al.id, am.id, rp.parent_id, rp.user_id, ai.invoice_date
            ),
            final_data as (
                select * from period1
                UNION
                select * from period2
                UNION
                select * from period3
                UNION
                select * from period4
                UNION
                select * from period5
                UNION
                select * from period6
                UNION
                select * from period7
                UNION
                select * from period8
                UNION
                select * from period9
                UNION
                select * from older
                UNION
                select * from undue_amount
                UNION
                select * from period10
                UNION
                select * from period11
                UNION
                select * from period12
                UNION
                select * from period13
                UNION
                select * from period14
                UNION
                select * from period15
                UNION
                select * from period16
                UNION
                select * from period17
                UNION
                select * from period18
                UNION
                select * from period19
                                   
            )
            select row_number() OVER () AS id, account_move_line_id,
            account_move_id, partner_id, parent_id, salesperson, invoice_id, 
            part1, part2, part3,
            part4, part5, part6, part7, part8, part9, part10, part11, part12, part13, part14, part15, part16, part17, part18, part19, older, undue, date_inv,
            (part1+part2+part3+part4+part5+part6+part7+older+undue) as total,
            (part8+part9+part18+part19) as total_
                from final_data
        """ % (day_30, day_0, receivable_type.id,
               day_60, day_30_1, receivable_type.id,
               day_90, day_60_1, receivable_type.id,
               day_120, day_90_1, receivable_type.id,
               day_150, day_120_1, receivable_type.id,
               day_180, day_150_1, receivable_type.id,
               day_210, day_180_1, receivable_type.id,
               day_180, day_0, receivable_type.id,
               day_180, receivable_type.id,
               day_210, receivable_type.id,
               day_0, receivable_type.id,
               year_1, receivable_type.id,
               year_1_5, receivable_type.id,
               year_2, receivable_type.id,
               year_2_5, receivable_type.id,
               year_3, receivable_type.id,
               year_3_5, receivable_type.id,
               year_4, receivable_type.id,
               day_120, receivable_type.id,
               day_150, receivable_type.id,
               day_150, day_0, receivable_type.id))
        result = self._cr.fetchall()

        start_row_data = 6
        for data in result:
            print(data)
            start_row_data += 1
            self._cr.execute("""
                select
                rp.name from res_partner rp
                where rp.id = %s""" % data[3])
            partner_name = self._cr.fetchall()
            self._cr.execute("""
                select
                am.name from account_move am
                where am.id = %s""" % data[2])
            move_name = self._cr.fetchall()
            print ('data...', data)
            worksheet.write(start_row_data, 0, data[30], align_value)
            worksheet.write(start_row_data, 1, move_name[0][0], align_value)
            worksheet.write(start_row_data, 2, partner_name[0][0], align_value)
            worksheet.write(start_row_data, 3, data[27], align_value)
            worksheet.write(start_row_data, 4, data[26], align_value)
            worksheet.write(start_row_data, 5, data[16], align_value)
            worksheet.write(start_row_data, 6, data[17], align_value)
            # worksheet.write(start_row_data, 7, data[32], align_value)

        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = 'Bank Report'
        # dt = 'From_' + str(self.to_date)
        out_wizard = self.env['xlsx.output.account'].create({
            'name': name + '.xlsx',
            'xls_output': base64.encodebytes(data)
        })
        view_id = self.env.ref('gts_aged_pivot_report.xlsx_output_form_accounting').id

        return {
            'type': 'ir.actions.act_window',
            'name': _(name),
            'res_model': 'xlsx.output.account',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }


class XlsxOutputAccount(models.TransientModel):
    _name = 'xlsx.output.account'
    _description = "XLSX Report Download"

    name = fields.Char('Name')
    xls_output = fields.Binary('Download', readonly=True)
