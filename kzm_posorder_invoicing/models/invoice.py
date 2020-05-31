# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    kzm_order_ids = fields.One2many('pos.order', 'kzm_invoice_client_id', string="Orders")
    orders = fields.Integer("Pos Orders", compute='_count_orders', store=1)

    @api.depends('kzm_order_ids')
    def _count_orders(self):
        for r in self:
            r.orders = len(r.kzm_order_ids)

    def see_orders(self):
        action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
        action['domain'] = [('id', 'in', [])]
        print(self.kzm_order_ids)
        if len(self.kzm_order_ids) == 1:
            action['views'] = [(self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')]
            action['res_id'] = self.kzm_order_ids.id
        elif len(self.kzm_order_ids) > 1:
            action['domain'] = [('id', 'in', self.kzm_order_ids.ids)]
            action['views'] = [(self.env.ref('point_of_sale.view_pos_order_tree').id, 'tree'),
                               (self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')]
        return action

    # def unlink(self):
    #     res = super(AccountInvoice, self).unlink()
    #     for r in res:
    #         r.
