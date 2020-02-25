# -*- coding: utf-8 -*-
{
    'name': 'POS User Control',
    'version': '11.0.0',
    'category': 'Point Of Sale',
    'author': 'Teqstars, updated by Abdelmajid Elhamdaoui',
    'website': 'https://teqstars.com',
    'support': 'elhamdaouiabdelmajid@gmail.com',
    'maintainer': 'Teqstars, Elhamdaoui Abdelmajid',
    'license': 'OPL-1',
    'summary': "To apply or restrict specific control for each user.",
    'depends': [
        'point_of_sale', 
        'aspl_pos_order_sync',
    ],
    'data': [
        'security/security.xml',
        'views/templates.xml',
        'views/res_users_view.xml',
        'views/pos_config.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/images/main_screen.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
}
