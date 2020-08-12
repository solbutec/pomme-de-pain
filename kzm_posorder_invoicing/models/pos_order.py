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
            print('yesss123ss')
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




class PosSession(models.Model):
    _inherit = 'pos.session'

    def _confirm_orders(self):
         # The government does not want PS orders that have not been
        # finalized into an NS before we close a session


        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id, default=session.config_id.journal_id.id)
            if not journal_id:
                raise UserError(_("You have to set a Sale Journal for the POS:%s") % (session.config_id.name,))
            if len(self.order_ids.filtered(lambda l: l.is_pos_client_order)) == len(self.order_ids):
                print(len(self.order_ids.filtered(lambda l: l.is_pos_client_order)))
                print(len(self.order_ids))
                return
            move = self.env['pos.order'].with_context(force_company=company_id)._create_account_move(session.start_at, session.name, int(journal_id), company_id)
            orders.with_context(force_company=company_id)._create_account_move_line(session, move)
            for order in session.order_ids.filtered(lambda o: o.state not in ['done', 'invoiced'] ):
                if order.state not in ('paid'):
                    raise UserError(
                        _("You cannot confirm all orders of this session, because they have not the 'paid' status.\n"
                          "{reference} is in state {state}, total amount: {total}, paid: {paid}").format(
                            reference=order.pos_reference or order.name,
                            state=order.state,
                            total=order.amount_total,
                            paid=order.amount_paid,
                        ))
                print(order.is_pos_client_order)
                if not order.is_pos_client_order:
                    print(order.is_pos_client_order)
                    order.action_pos_order_done()
            orders_to_reconcile = session.order_ids._filtered_for_reconciliation()
            orders_to_reconcile.sudo()._reconcile_payments()







