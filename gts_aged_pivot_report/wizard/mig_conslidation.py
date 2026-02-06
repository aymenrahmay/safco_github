from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
class AgedPayableReportWiz(models.TransientModel):
    _name = 'aged.payable.report.wiz'

    to_date = fields.Date('To Date', default=fields.Date.context_today, required=True)

class AgedReportWiz(models.TransientModel):
    _name = 'aged.report.wiz'

    to_date = fields.Date('To Date', default=fields.Date.context_today, required=True)
