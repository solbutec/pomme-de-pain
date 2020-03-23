# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'POS Combo',
    'category': 'Point of Sale',
    'summary': 'This module allows user to use combo feature in restaurant.',
    'description': """
This module allows user to use combo feature in restaurant
""",
    'author': 'Elhamdaoui Abdelmajid, Karizma Conseil',
    'website': 'http://karizma-conseil.com',
    'price': 25,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': [
        'base',
        'pos_restaurant',
        #'kzm_pos_supplements',
        'mrp',
        'aspl_pos_order_sync',
    ],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'views/aspl_pos_combo.xml',
        'views/supplements_views.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
