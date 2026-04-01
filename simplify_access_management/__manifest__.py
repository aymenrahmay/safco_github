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
    'version': '19.0.2.2.9',
    'sequence': 5,
    'author': 'Terabits Technolab',
    'license': 'OPL-1',
    'category': 'Services',
    'website': 'https://www.terabits.xyz/apps/18.0/simplify_access_management',
    'summary': """All In One Access Management App for setting the correct access rights for fields, models, menus, views for a
        """,
    "price": "392.97",
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
        'simplify_access_management/static/src/js/action_menus.js',
        'simplify_access_management/static/src/js/hide_chatter.js',
        'simplify_access_management/static/src/js/cog_menu.js',
        'simplify_access_management/static/src/js/list_spreadsheet.js',
        'simplify_access_management/static/src/js/form_controller.js',
        'simplify_access_management/static/src/xml/mailChatter.xml',
        'simplify_access_management/static/src/js/model_field_selector.js',
        'simplify_access_management/static/src/js/search_bar_menu.js',
        'simplify_access_management/static/src/js/custom_group_by_item.js',
        'simplify_access_management/static/src/xml/custom_group_by_item.xml',
        'simplify_access_management/static/src/js/remove_archive_with_rule.js',

    ],
},

    'depends': ['base','mail','web','advanced_web_domain_widget'],
    #'post_init_hook': 'post_install_action_dup_hook',
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.terabits.xyz/request_demo?source=index&version=19&app=simplify_access_management',
}
