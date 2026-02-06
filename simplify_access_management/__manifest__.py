# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2023-25
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can't redistribute/reshare/recreate it for any purpose.
#
#################################################################################

{
    'name': 'Simplify Access Management',
    'version': '16.0.17.14.20',
    'sequence': 5,
    'author': 'Terabits Technolab',
    'license': 'OPL-1',
    'category': 'Services',
    'website': 'https://www.terabits.xyz/apps/16.0/simplify_access_management',
    'summary': """All In One Access Management App for setting the correct access rights for fields, models, menus, views for any module and for any user.
        All in one access management App,
        Easier then Record rules setup,
        Centralize access rules,
        User wise access rules,
        
        Multi Company supported.
        """,

    'description': """
        All In One Access Management App for setting the correct access rights for fields, models, menus, views for any module and for any user.
    """,
    "images": ["static/description/banner.gif"],
    "price": "342.97",
    "currency": "USD",
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/view_data.xml',
        'views/access_management_view.xml',
        'views/res_users_view.xml',
        'views/store_model_nodes_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/simplify_access_management/static/src/js/action_menus.js',
            '/simplify_access_management/static/src/js/hide_chatter.js',
            '/simplify_access_management/static/src/js/hide_export.js',
            '/simplify_access_management/static/src/js/custom_filter_item.js',
            '/simplify_access_management/static/src/js/pivot_grp_menu.js',
        ],

    },
    'depends': ['web', 'advanced_web_domain_widget'],
    'post_init_hook': 'post_install_action_dup_hook',
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.terabits.xyz/request_demo?source=index&version=16&app=simplify_access_management',
}
