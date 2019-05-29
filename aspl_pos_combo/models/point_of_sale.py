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
    enable_supplement = fields.Boolean(string="Supplement", default=False)


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        new_order_line = []
        process_line = partial(self.env['pos.order.line']._order_line_fields)
        order_lines = [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False

        for order_line in order_lines:
            new_order_line.append(order_line)
            if 'note' in order_line[2]:
                res["note"] = (res['note']+order_line[2].get('note','')) if 'note' in res else order_line[2].get('note','')
            if 'combo_ext_line_info' in order_line[2]:
                own_pro_list = [process_line(l) for l in order_line[2]['combo_ext_line_info']] if order_line[2][
                    'combo_ext_line_info'] else False
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
    pos_price_tot = fields.Float("prix total", compute='_compute_total', store=True)
    price_supplement = fields.Float("prix supplement", help="price in case it is a supplement")

    @api.depends('price_supplement', 'list_price')
    def _compute_total(self):
        for record in self:
            record.pos_price_tot = record.price_supplement + record.list_price


class ProductCombo(models.Model):
    _name = 'product.combo'

    product_tmpl_id = fields.Many2one('product.template')
    require = fields.Boolean("Required", Help="Don't select it if you want to make it optional")
    pos_category_id = fields.Many2one('pos.category', "Categories")
    #product_ids = fields.Many2many('product.product', string="Products")
    product_ids = fields.One2many('kzm.pos.supplement', 'product_combo_id', string="Products")
    no_of_items = fields.Integer("No. of Items", default=1)

    @api.onchange('require')
    def onchage_require(self):
        for o in self:
            if o.require:
                o.pos_category_id = False



    # @api.onchange('pos_category_id')
    # def onchage_pos_category_id(self):
    #     domain=[('available_in_pos', '=', True)]
    #     if self.pos_category_id:
    #         domain.append(('pos_categ_id','child_of',self.pos_category_id.id))
    #     return {
    #         'domain': {
    #             'product_ids': {
    #                 'product_id': domain,
    #             }
    #         },
    #     }


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_splmnt = fields.Boolean("Is supplement", default=False)
    real_supplement_price = fields.Float("Real supplement price")


    @api.model
    def get_compute_amount_line_all(self, values):
        if values.get('order_id', False) and not (values.get('price_subtotal')):
            order_id = self.env['pos.order'].browse(values['order_id'])
            taxes = []
            for t in values.get('tax_ids', []):
                taxes += t[2]
            tax_ids = self.env['account.tax'].browse(taxes)
            product_id = self.env['product.product'].browse([values.get('product_id', 0)])

            fpos = order_id.fiscal_position_id
            tax_ids_after_fiscal_position = fpos.map_tax(tax_ids, product_id,
                                                         order_id.partner_id) if fpos else tax_ids
            price = values.get('price_unit', 0) * (1 - (values.get('discount', 0) or 0.0) / 100.0)
            taxes = tax_ids_after_fiscal_position.compute_all(price, order_id.pricelist_id.currency_id,
                                                              values.get('qty', 0),
                                                              product=product_id, partner=order_id.partner_id)
            return {
                'price_subtotal_incl': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            }
        return {}

    @api.model
    def create(self, vals):
        values = vals.copy()
        if values.get('price', 'NOO') != 'NOO':
            values['price_unit'] = values.get('price', 0)
            del values['price']
        if values.get('combo_ext_line_info', 'NOO') != 'NOO':
            del values['combo_ext_line_info']
        if values.get('note', 'MJ-@-78') != 'MJ-@-78':
            del values['note']



        if not values.get('price_subtotal', False):
            nw_vls = self.env['pos.order.line'].get_compute_amount_line_all(values)
            values.update(nw_vls)

        if values.get('price_unit', 0) == 0:
            values['is_splmnt'] = True

        from pprint import pprint
        res = super(PosOrderLine, self).create(values)
        return res

        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


class PosSupplement(models.Model):
    _name = 'kzm.pos.supplement'

    @api.depends('product_id')
    def compute_name_prod(self):
        for o in self:
           o.name = o.product_id.name

    product_id = fields.Many2one("product.product", "Produit", required=True)
    price_supplement = fields.Float("Price supplement", default=0)
    name = fields.Char("Name", compute= compute_name_prod, store=True)
    product_combo_id = fields.Many2one("product.combo", "Combo")

    _sql_constraints = [('uniq_prod_combo', 'unique(product_combo_id, product_id)', "The product has already chosen !")]