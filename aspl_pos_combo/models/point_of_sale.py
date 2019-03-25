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

from openerp import models, fields, api, _
from functools import partial

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_combo = fields.Boolean('Enable Combo')

class PosOrder(models.Model):
    _inherit="pos.order"

    def _order_fields(self,ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        new_order_line = []
        process_line = partial(self.env['pos.order.line']._order_line_fields)
        order_lines = [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False
        for order_line in order_lines:
            new_order_line.append(order_line)
            if 'combo_ext_line_info' in order_line[2]:
                own_pro_list = [process_line(l) for l in order_line[2]['combo_ext_line_info']] if order_line[2]['combo_ext_line_info'] else False
                if own_pro_list:
                    for own in own_pro_list:
                        new_order_line.append(own)
        res.update({
            'lines': new_order_line,
        })
        return res

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_combo = fields.Boolean("Is Combo")
    product_combo_ids = fields.One2many('product.combo', 'product_tmpl_id')

class ProductCombo(models.Model):
    _name = 'product.combo'
    
    product_tmpl_id = fields.Many2one('product.template') 
    require = fields.Boolean("Required", Help="Don't select it if you want to make it optional")
    pos_category_id = fields.Many2one('pos.category', "Categories")
    product_ids = fields.Many2many('product.product',string="Products")
    no_of_items = fields.Integer("No. of Items", default= 1)

    @api.onchange('require')
    def onchage_require(self):
        if self.require:
            self.pos_category_id = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: