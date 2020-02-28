# -*- coding: utf-8 -*-
{
    'name': "PDP REPORTING",
    'summary': """Module for pdp reportings""",
    'description': """Generate reportings for PDP POS""",
    'author': "Elhamdaoui Abdelmajid, Karizma Conseil",
    'website': "http://karizma-conseil.com/",
    'category': 'Point of sale',
    'version': '12.0',
    # any module necessary for this one to work correctly
    'depends': [
        'point_of_sale',
        'amh_payement_currencies',  
        'aspl_pos_order_sync',
        'pos_customer_display',  
        'pos_user_control',
        'aspl_pos_combo',
        'pos_tracking_actions', 
        'pos_user_restrict',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'views/pos_config_views.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/pdp_reporting.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
