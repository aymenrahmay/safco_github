# -*- coding: utf-8 -*-
{
    'name': 'MRP safco',
    'version': '1.0',
    'category': 'MRP',
    'description': "MRP safco ",
    'author': "Aymen RAHMANI",
    'depends': ['base','sale','mrp','mrp_account_enterprise'],
    'data': [
            'views/views_model.xml',
            'views/z_mrp_report.xml',
            'views/z_mrp_header.xml',
            'views/z_mrp_production_order_report.xml',
            'views/z_mrp_process_batch_card_report.xml',
            'views/z_mrp_bom_request_report.xml',
            'views/z_mrp_product_analysis_report.xml',
            'views/z_mrp_product_release_certificate_report.xml',
            'views/z_mrp_tree_report.xml',
            'views/report.xml',
            ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
