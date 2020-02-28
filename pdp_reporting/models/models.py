# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint


# class PosConfig(models.Model):
#     _inherit = 'pos.config'


# class PosConfigWizard(models.TransientModel):
#     _name = 'pos.config.wizard'

#     debut_date = fields.Datetime("Debut date")
#     end_date = fields.Datetime("End date")
#     type = fields.Selection([('by_op', "By operator"), ('by_pay', "By payment"), ('by_ord', "By order")],
#                             default='by_op')
#     cashier_id = fields.Many2one('res.users', string="Cashier")

#     @api.multi
#     def action_print(self):
#         print(self.debut_date)
#         print(self.end_date)
#         print(self.type)
#         print(self.cashier_id)
#         rapport = self.env.ref('maphar_loan_advance.pret_avance_report_report')
#         pos_orders = self.env['pos.order']
#         date_domain = [('date_order', '>=', self.debut_date), ('date_order', '<=', self.end_date)]
#         if self.type == 'by_op':
#             domain = date_domain + [('user_id', '=', self.cashier_id.id)]
#             orders = pos_orders.search(domain)
#             pprint(orders)
#             rapport.report_action(orders, config=False)
#         elif self.type == 'by_pay':
#             pass
#         elif self.type == 'by_ord':
#             pass
