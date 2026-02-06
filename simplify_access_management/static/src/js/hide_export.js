// /* @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { session } from "@web/session";
const { patch } = require("web.utils");
const { onWillStart } = owl;
var rpc = require("web.rpc");

patch(ListController.prototype, "simplify_access_management.ListController", {
    setup() {
        this._super();
        onWillStart(async () => {
            await this.is_hide_export();
        });
    },
    async is_hide_export() {
        let model = this.props.resModel;

        let cids = this.userService.context.allowed_company_ids
        let sam_hide_export = await rpc.query({
            model: "access.management",
            method: "get_remove_options",
            args: [cids, model],
        });

        if (sam_hide_export.includes('export')) {
            this.isExportEnable = false;
        } else {
            this.isExportEnable = await this.userService.hasGroup("base.group_allow_export");
        }
    }
})