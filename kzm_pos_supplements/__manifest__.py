# -*- coding: utf-8 -*-
{
    'name': "POS SUPPLEMENTS COMBO",

    'summary': """
        Add the supplements in some menus.
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Bouchra & Elhamdaoui",
    'website': "http://www.karizma.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'point_of_sale',
    ],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/supplements_views.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [
        # 'demo/demo.xml',
        #'views/test.xml'
    ],
}
