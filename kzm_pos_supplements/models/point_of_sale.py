# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_supplement = fields.Boolean(string="Supplement", default=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    with_supplements = fields.Boolean("Have supplements", default=False)
    pos_supplement_ids = fields.One2many('kzm.pos.supplement', 'product_tmpl_id', "Supplements", ondelate="cascade")


class PosSupplement(models.Model):
    _name = 'kzm.pos.supplement'

    product_tmpl_id = fields.Many2one("product.template", "Combo product", required=True)
    product_id = fields.Many2one("product.product", "Produit", required=True)
    price_unit = fields.Float("Price", default=lambda s: s.product_id.list_price)

    @api.onchange("product_id")
    def on_change_product(self):
        for o in self:
            if o.product_id.list_price:
                o.price_unit = o.product_id.list_price
