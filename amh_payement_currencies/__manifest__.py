# -*- coding: utf-8 -*-
{
    'name': 'KZM POS PAYMENT CURRENCY',
    'version': '1.0',
    'author': 'Elhamdaoui Abdelmajid, KARIZMA CONSEIL',
    'summary': "POS Payment with currencies",
    'description': "Allow salesperson/Cashier to do payment with other currency (convert en main currency)",
    'category': 'Point Of Sale',
    'website': 'http://www.karizma-conseil.com',
    'depends': [
        'base',
        'point_of_sale',
        'account',
    ],
    'price': 20.00,
    'currency': 'EUR',
    'images': [
         'static/description/main_screenshot.png',
     ],
    'data': [
        'views/pos_assets.xml',
        'views/pos_view.xml'
    ],
     'qweb': [
        'static/src/xml/pos.xml'
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
