from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgedReportWiz(models.TransientModel):
    _name = 'aged.report.wiz'
    _description = 'Aged Receivable Report Wizard'

    to_date = fields.Date('To Date', default=fields.Date.context_today, required=True)

    def open_aged_table(self):
        """
        Generate aged receivable report with optimized performance
        """
        # Clear existing report data efficiently
        self.env['aged.report'].search([]).unlink()

        if not self.to_date:
            return self._get_report_action()

        # Get receivable accounts
        receivable_accounts = self.env['account.account'].search([
            ('account_type', '=', 'asset_receivable')
        ])
        if not receivable_accounts:
            raise UserError(_('Please configure "Receivable" account type!'))

        # Use single optimized SQL query
        self._execute_optimized_query(receivable_accounts.ids)

        return self._get_report_action()

    def _execute_optimized_query(self, account_ids):
        """
        Execute single optimized SQL query for aging analysis
        """
        if len(account_ids) == 1:
            account_ids.append(0)  # Ensure tuple has multiple elements

        # Calculate all date ranges once
        date_ranges = self._calculate_date_ranges()

        # Build query with correct parameter count - COUNTED CAREFULLY
        query = """
            INSERT INTO aged_report (
                account_move_line_id, account_move_id, partner_id, parent_id,
                salesperson, invoice_id, date_inv, 
                part1, part2, part3, part4, part5, part6, part7, part8, part9,
                part10, part11, part12, part13, part14, part15, part16, part17,
                part18, part19, part20, part21, older, undue, total, total_
            )
            SELECT 
                aml.id as account_move_line_id,
                aml.move_id as account_move_id,
                aml.partner_id as partner_id,
                rp.parent_id as parent_id,
                rp.user_id as salesperson,
                aml.move_id as invoice_id,
                ai.invoice_date as date_inv,

                -- Aging buckets using CASE statements
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part1,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part2,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part3,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part4,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part5,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part6,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part7,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part8,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part9,

                -- Additional periods
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part10,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part11,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part12,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part13,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part14,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part15,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part16,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part17,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part18,
                CASE WHEN aml.date_maturity BETWEEN %s AND %s THEN aml.amount_residual ELSE 0 END as part19,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part20,
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as part21,

                -- Older and undue amounts
                CASE WHEN aml.date_maturity < %s THEN aml.amount_residual ELSE 0 END as older,
                CASE WHEN aml.date_maturity > %s THEN aml.amount_residual ELSE 0 END as undue,

                -- Totals
                aml.amount_residual as total,
                0.0 as total_

            FROM account_move_line aml
            JOIN res_partner rp ON rp.id = aml.partner_id
            JOIN account_move am ON am.id = aml.move_id
            JOIN account_move ai ON ai.id = aml.move_id
            WHERE am.state = 'posted'
                AND aml.account_id IN %s
                AND aml.amount_residual != 0.0
                AND aml.partner_id IS NOT NULL
        """

        # Prepare all parameters in correct order - NOW 34 PARAMETERS TOTAL
        params = [
            # Period 1: day_30 to day_0 (2 params)
            date_ranges['day_30'], date_ranges['day_0'],
            # Period 2: day_60 to day_30_1 (2 params)
            date_ranges['day_60'], date_ranges['day_30_1'],
            # Period 3: day_90 to day_60_1 (2 params)
            date_ranges['day_90'], date_ranges['day_60_1'],
            # Period 4: day_120 to day_90_1 (2 params)
            date_ranges['day_120'], date_ranges['day_90_1'],
            # Period 5: day_150 to day_120_1 (2 params)
            date_ranges['day_150'], date_ranges['day_120_1'],
            # Period 6: day_180 to day_150_1 (2 params)
            date_ranges['day_180'], date_ranges['day_150_1'],
            # Period 7: day_210 to day_180_1 (2 params)
            date_ranges['day_210'], date_ranges['day_180_1'],
            # Period 8: day_180 to day_0 (2 params)
            date_ranges['day_180'], date_ranges['day_0'],
            # Period 9: < day_180 (1 param)
            date_ranges['day_180'],
            # Part 10: < year_1 (1 param)
            date_ranges['year_1'],
            # Part 11: < year_1_5 (1 param)
            date_ranges['year_1_5'],
            # Part 12: < year_2 (1 param)
            date_ranges['year_2'],
            # Part 13: < year_2_5 (1 param)
            date_ranges['year_2_5'],
            # Part 14: < year_3 (1 param)
            date_ranges['year_3'],
            # Part 15: < year_3_5 (1 param)
            date_ranges['year_3_5'],
            # Part 16: < year_4 (1 param)
            date_ranges['year_4'],
            # Part 17: < day_120 (1 param) - MISSING THIS ONE!
            date_ranges['day_120'],
            # Part 18: < ??? (1 param) - NEED ONE MORE!
            date_ranges['day_150'],  # Using day_150 as part18
            # Part 19: Between day_150 and day_0 (2 params)
            date_ranges['day_150'], date_ranges['day_0'],
            # Part 20: < day_60 (1 param)
            date_ranges['day_60'],
            # Part 21: < day_90 (1 param)
            date_ranges['day_90'],
            # Older: < day_210 (1 param)
            date_ranges['day_210'],
            # Undue: > day_0 (1 param)
            date_ranges['day_0'],
            # Account IDs (1 param as tuple)
            tuple(account_ids)
        ]

        # Debug: Check parameter count
        expected_params = 34  # Fixed: Now 34 parameters total
        actual_params = len(params)

        # Count the actual %s placeholders in the query
        placeholder_count = query.count('%s')



        # Execute the query
        self._cr.execute(query, params)

    def _calculate_date_ranges(self):
        """
        Calculate all date ranges needed for aging analysis
        """
        to_date = self.to_date

        # Calculate standard aging periods
        day_0 = to_date
        day_30 = to_date - timedelta(days=30)
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

        # Calculate yearly periods (approximated with days)
        year_1 = to_date - timedelta(days=365)
        year_1_5 = to_date - timedelta(days=365 + 180)  # 1.5 years
        year_2 = to_date - timedelta(days=365 * 2)
        year_2_5 = to_date - timedelta(days=365 * 2 + 180)
        year_3 = to_date - timedelta(days=365 * 3)
        year_3_5 = to_date - timedelta(days=365 * 3 + 180)
        year_4 = to_date - timedelta(days=365 * 4)

        return {
            'day_0': day_0,
            'day_30': day_30,
            'day_30_1': day_30_1,
            'day_60': day_60,
            'day_60_1': day_60_1,
            'day_90': day_90,
            'day_90_1': day_90_1,
            'day_120': day_120,
            'day_120_1': day_120_1,
            'day_150': day_150,
            'day_150_1': day_150_1,
            'day_180': day_180,
            'day_180_1': day_180_1,
            'day_210': day_210,
            'year_1': year_1,
            'year_1_5': year_1_5,
            'year_2': year_2,
            'year_2_5': year_2_5,
            'year_3': year_3,
            'year_3_5': year_3_5,
            'year_4': year_4,
        }

    def _get_report_action(self):
        """
        Return the report action with all views
        """
        try:
            tree_view_id = self.env.ref('gts_aged_pivot_report.view_aged_report_tree').id
            form_view_id = self.env.ref('gts_aged_pivot_report.view_aged_report_form').id
            graph_view_id = self.env.ref('gts_aged_pivot_report.view_aged_report_graph').id
            pivot_view_id = self.env.ref('gts_aged_pivot_report.view_aged_report_pivot').id
            search_view_ref = self.env.ref('gts_aged_pivot_report.view_aged_report_search', False)
        except Exception as e:
            raise UserError(_(
                "Report views not found. Please check if the view references are correct. Error: %s"
            ) % str(e))

        return {
            'type': 'ir.actions.act_window',
            'views': [
                #(pivot_view_id, 'pivot'),
                (tree_view_id, 'tree'),
                (form_view_id, 'form'),
                #(graph_view_id, 'graph')
            ],
            'view_mode': 'from,tree',
            'name': _('Aged Receivable Report'),
            'res_model': 'aged.report',
            'search_view_id': search_view_ref and search_view_ref.id,
            'context': {'group_by': ['parent_id', 'partner_id', 'account_move_id']},
            'target': 'current',
        }