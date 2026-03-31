{
    "name": "Stock Safco",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "SAFCO stock customizations",
    "description": "SAFCO stock customizations for Odoo 19.",
    "author": "Aymen RAHMANI",
    "license": "LGPL-3",
    "depends": ["base", "sale", "stock"],
    "data": [
        "views/view_model.xml",
        "wizard/update_effective_date_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
