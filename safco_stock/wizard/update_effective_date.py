from odoo import _, fields, models
from odoo.exceptions import UserError


class UpdateEffectiveDate(models.TransientModel):
    _name = "update.effective.date"
    _description = "Update Picking Effective Date"

    to_apply_date = fields.Datetime(string="Date to apply", required=True)

    def update_effective_date(self):
        self.ensure_one()
        if self.env.context.get("active_model") != "stock.picking":
            raise UserError(_("This wizard can only be used from a transfer."))

        pickings = self.env["stock.picking"].browse(self.env.context.get("active_ids", []))
        if not pickings and self.env.context.get("active_id"):
            pickings = self.env["stock.picking"].browse(self.env.context["active_id"])

        if not pickings:
            raise UserError(_("No transfer was selected."))

        done_pickings = pickings.filtered(lambda p: p.state == "done")
        if not done_pickings:
            raise UserError(_("Only done transfers can have their effective date updated."))

        done_pickings.write({"date_done": self.to_apply_date})
        done_pickings.move_ids_without_package.write({"date": self.to_apply_date})
        done_pickings.move_line_ids.write({"date": self.to_apply_date})

        return {"type": "ir.actions.act_window_close"}
