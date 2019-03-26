# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

   # test = fields.Boolean(string="TEEST" , default=False)
    supplement = fields.Boolean(string="supplement", default=False)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    with_supplements = fields.Boolean("with_supplements")