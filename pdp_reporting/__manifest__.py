# -*- coding: utf-8 -*-
{
    'name': "PDP REPORTING",
    'summary': """Module for pdp reportings""",
    'description': """Generate reportings for PDP POS""",
    'author': "Assabe POLO, PYVAL",
    'website': "https://pyval.com/",
    'category': 'Uncategorized',
    'version': '12.0',
    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        # 'data/crm_lead_code_sequence.xml',
        # 'data/crm_lead_lost_reason.xml',
        'views/pos_config_views.xml',
        # 'views/crm_lead_views.xml',
        # 'views/sale_order_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
