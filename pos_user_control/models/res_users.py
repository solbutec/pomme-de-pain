# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = "res.users"

    has_pos_price_control = fields.Boolean("Price Control")
    has_pos_qty_control = fields.Boolean("Quantity Control")
    has_pos_back_backspace_control = fields.Boolean("Backspace Control")
    has_pos_delete_order_control = fields.Boolean("Remove Order Control")