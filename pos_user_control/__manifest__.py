# -*- coding: utf-8 -*-
{
    'name': 'POS User Control',
    'version': '11.0.0',
    'category': 'Point Of Sale',
    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    'license': 'OPL-1',
    'summary': "To apply or restrict specific control for each user.",
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
        'views/res_users_view.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/images/main_screen.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0.0,
    'currency': 'EUR',
}
