# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    pos_history_operations = fields.Text("Traces")

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['pos_history_operations'] = ui_order.get('pos_history_operations', "")
        return res