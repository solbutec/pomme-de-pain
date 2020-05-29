# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_pos_client_order = fields.Boolean("Pos client order", compute='get_client', store=1)
    kzm_invoice_client_id = fields.Many2one('account.invoice', string="Client invoice")

    kzm_pos_client_id = fields.Many2one('res.partner', string="KZM Client", compute='get_client', store=1)

    @api.depends('partner_id')
    def get_client(self):
        for r in self:
            r.kzm_pos_client_id = r.partner_id.parent_id or r.partner_id
            # r.is_pos_client_order = r.is_pos_client_order

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

        prepare_invoice = orders[0]._prepare_invoice()
        invoice_type = 'out_invoice' if sum([order.amount_total for order in orders]) >= 0 else 'out_refund'
        print('======================')
        print(prepare_invoice)
        print('=======================')
        prepare_invoice['partner_id'] = orders[0].kzm_pos_client_id
        prepare_invoice['type'] = invoice_type
        prepare_invoice['date_invoice'] = fields.Date.today()

        invoice = Invoice.new(prepare_invoice)
        invoice._onchange_partner_id()
        invoice.fiscal_position_id = orders[0].fiscal_position_id

        inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
        new_invoice = Invoice.with_context(local_context).sudo().create(inv)
        # message = _(
        #     "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
        #           order.id, order.name)
        # new_invoice.message_post(body=message)
        orders.write({'kzm_invoice_client_id': new_invoice.id, 'state': 'invoiced'})
        Invoice += new_invoice
        lines = []
        for order in orders:
            lines += order.lines

        for line in lines:
            self.with_context(local_context)._action_create_invoice_line(line, new_invoice.id)

        new_invoice.with_context(local_context).sudo().compute_taxes()
        orders.sudo().write({'state': 'invoiced'})

        if not Invoice:
            return {}

        # return {
        #     'name': _('Customer Invoice'),
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('account.invoice_form').id,
        #     'res_model': 'account.invoice',
        #     'context': "{'type':'out_invoice'}",
        #     'type': 'ir.actions.act_window',
        #     'nodestroy': True,
        #     'target': 'current',
        #     'res_id': Invoice and Invoice.ids[0] or False,
        # }

        # invoice_id = self.env['account.invoice'].create({
        #     'partner_id': self[0].demandeur_parent.id,
        #     'ticket_ids': [(6, 0, self.ids)]
        # })
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['res_id'] = new_invoice.id
        return action





