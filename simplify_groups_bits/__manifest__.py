# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2021-23
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can't redistribute/reshare/recreate it for any purpose.
#
#################################################################################

{
    'name': 'Simplify Group Access',
    'version': '16.0.2.0.0',
    'summary': """ The Access Group feature simplifies access management by allowing you to create rules for specific groups of users """,
    'sequence': 10,
    'author': 'Terabits Technolab',
    'license': 'OPL-1',
    'category': 'Services',
    'website': 'https://www.terabits.xyz/apps/16.0/simplify_groups_bits',
    'description': """
        The Access Group feature simplifies access management by allowing you to create rules for specific groups of users
        """,
    'depends': ['simplify_access_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/access_groups_view.xml',
        'views/access_management_view.xml',
    ],
    "price": "99.99",
    "currency": "USD",
    'live_test_url': 'https://www.terabits.xyz/request_demo?source=index&version=16&app=simplify_access_management',
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}