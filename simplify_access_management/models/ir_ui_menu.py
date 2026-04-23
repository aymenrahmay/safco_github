from odoo import api, fields, models
from odoo.http import request


class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _get_hidden_menu_ids_for_current_user(self):
        company_id = self.env.company.id
        if request and getattr(request, 'httprequest', None):
            cids = request.httprequest.cookies.get('cids')
            if cids:
                try:
                    company_id = int(cids.split('-')[0])
                except (TypeError, ValueError):
                    company_id = self.env.company.id

        access_rules = self.env.user.access_management_ids.filtered(
            lambda line: line.is_apply_on_without_company or company_id in line.company_ids.ids
        )
        return access_rules.mapped('hide_menu_ids').ids


    @api.model
    def _visible_menu_ids(self, debug=False):
        visible_ids = set(super()._visible_menu_ids(debug=debug))
        hidden_menu_ids = self._get_hidden_menu_ids_for_current_user()
        if hidden_menu_ids:
            visible_ids.difference_update(hidden_menu_ids)
        return frozenset(visible_ids)


    def _load_menus_blacklist(self):
        hidden_menu_ids = self._get_hidden_menu_ids_for_current_user()
        return list(set(super()._load_menus_blacklist()) | set(hidden_menu_ids))

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ir_ui_menu, self).create(vals_list)
        menu_item_obj = self.env['menu.item'].sudo()
        for record in res:
            menu_item_obj.create({'name': record.display_name, 'menu_id': record.id})
        return res

    def unlink(self):
        menu_item_obj = self.env['menu.item'].sudo()
        for record in self:
            menu_item_obj.search([('menu_id', '=', record.id)]).unlink()
        return super(ir_ui_menu, self).unlink()
