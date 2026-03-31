# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_qty = fields.Float(string="Quantity", default=1.0, digits=(16, 7), required=True)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    vise_number = fields.Char(string="Vessel number")
    total_qty = fields.Float(string="Total Qty", compute="_compute_total_qty", store=True)
    total_mixing_time = fields.Char(string="Total mixing time")
    verified_by = fields.Char(string="Verified by")
    mixing_operator = fields.Char(string="Mixing operator")
    confirmation_date_time = fields.Datetime(string="Confirmation date time")
    remarks = fields.Char(string="Remarks")
    ph = fields.Char(string="PH")
    sp = fields.Char(string="Sp. Gravity")
    color = fields.Char(string="Color")
    od = fields.Char(string="ODour")
    gtavity = fields.Char(string="Refractive")
    other = fields.Char(string="Other")
    refractive = fields.Char(string="Refractive")
    status = fields.Selection(
        [
            ("pass", "Pass"),
            ("fail", "Fail"),
        ],
        string="Status",
    )

    @api.depends("move_raw_ids.product_uom_qty")
    def _compute_total_qty(self):
        for production in self:
            production.total_qty = sum(production.move_raw_ids.mapped("product_uom_qty"))
