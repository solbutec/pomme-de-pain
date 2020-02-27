# -*- coding: utf-8 -*-
{
    'name': 'POS Tracking actions',
    'version': '11.0.0',
    'category': 'Point Of Sale',
    'author': 'Abdelmajid Elhamdaoui, karizma-conseil',
    'website': 'http://karizma-conseil.com',
    'support': 'elhamdaouiabdelmajid@gmail.com',
    'maintainer': 'karizma-conseil, Elhamdaoui Abdelmajid',
    'license': 'OPL-1',
    'summary': "To track what happens on Pos interface, delete pos.line or update price ...",
    'depends': [
        'point_of_sale', 
        'aspl_pos_combo',
        'pos_user_control',
        'pos_customer_display',
    ],
    'data': [
        'views/pos_order.xml',
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/images/main_screen.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
}
