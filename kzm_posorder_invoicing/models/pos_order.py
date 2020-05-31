# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_pos_client_order = fields.Boolean("Pos client order", compute='get_client', store=1)
    kzm_invoice_client_id = fields.Many2one('account.invoice', string="Client invoice")

    kzm_pos_client_id = fields.Many2one('res.partner', string="KZM Client", compute='get_client', store=1)

    @api.depends('partner_id')
    def get_client(self):
        for r in self:
            print('yesssss')
            r.kzm_pos_client_id = r.partner_id.parent_id or r.partner_id
            r.is_pos_client_order = r.kzm_pos_client_id

    @api.multi
    def action_create_invoices(self):
        orders = self.env['pos.order'].browse(self._context.get('active_ids', []))
        print(orders)

        Invoice = self.env['account.invoice']
        local_context = dict(self.env.context, force_company=orders[0].company_id.id, company_id=orders[0].company_id.id)

        for order in orders:
            # Force company for all SUPERUSER_ID action
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

        partners = list(set([l.kzm_pos_client_id.id for l in orders]))

        print(partners)

        if len(partners) > 1:
            raise UserError(_('The customer partner must be unique.'))


        prepare_invoice = orders[0]._prepare_invoice()
        invoice_type = 'out_invoice' if sum([order.amount_total for order in orders]) >= 0 else 'out_refund'
        print('======================')
        print(prepare_invoice)
        print('=======================')
        prepare_invoice['partner_id'] = orders[0].kzm_pos_client_id
        prepare_invoice['type'] = invoice_type
        prepare_invoice['date_invoice'] = fields.Date.today()
        prepare_invoice['origin'] = '-'.join([order.name for order in orders])
        prepare_invoice['reference'] = '-'.join([order.name for order in orders])
        prepare_invoice['name'] = '-'.join([order.name for order in orders])
        prepare_invoice['user_id'] = self.env.uid

        invoice = Invoice.new(prepare_invoice)
        invoice._onchange_partner_id()
        invoice.fiscal_position_id = orders[0].fiscal_position_id

        inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
        new_invoice = Invoice.with_context(local_context).sudo().create(inv)
        new_invoice.kzm_order_ids = [(6, 0, orders.ids)]
        new_invoice._count_orders()

        Invoice += new_invoice
        # lines = []
        for order in orders:
            order.write({'kzm_invoice_client_id': new_invoice.id, 'invoice_id': new_invoice.id, 'state': 'invoiced'})
            # lines += order.lines
            for line in order.lines:
                order.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

        new_invoice.with_context(local_context).sudo().compute_taxes()
        for order in orders:
            order.sudo().write({'state': 'invoiced'})

        if not Invoice:
            return {}

        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = Invoice and Invoice.ids[0] or False
        action['context'] = {'type':'out_invoice'}
        return action





