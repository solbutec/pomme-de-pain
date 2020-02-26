# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = "pos.order"

    pos_history_operations = fields.Text("Traces")