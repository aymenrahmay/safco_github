from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_picking_update_effective_date(self):
        self.ensure_one()
        return {
            "name": _("Update Effective Date"),
            "type": "ir.actions.act_window",
            "res_model": "update.effective.date",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_to_apply_date": self.date_done or self.scheduled_date,
                "active_id": self.id,
                "active_ids": self.ids,
                "active_model": self._name,
            },
        }
