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
            if not order.invoice_group:
                raise UserError(_(
                    "The shop of %s has not the invoice feature activate. Please contact the administrator for further explanations" % order.name))
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

    def _create_account_move(self, dt, ref, journal_id, company_id):
        date_tz_user = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(dt))
        date_tz_user = fields.Date.to_string(date_tz_user)

        return self.env['account.move'].sudo().create({'ref': ref, 'journal_id': journal_id, 'date': date_tz_user})




class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def action_pos_session_close(self):
        # Close CashBox
        for session in self:
            company_id = session.config_id.company_id.id
            ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
            ctx_notrack = dict(ctx, mail_notrack=True)
            for st in session.statement_ids:
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.user_has_groups("point_of_sale.group_pos_manager"):
                        raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise UserError(_("The journal type for your payment method should be bank or cash."))
                if not st.journal_id.id == self.env.ref('kzm_posorder_invoicing.custom_payment').id:
                    print(st.journal_id.id)
                    print(self.env.ref('kzm_posorder_invoicing.custom_payment').id)
                    print("jjjjjjjjjjjj")
                    st.with_context(ctx_notrack).sudo().button_confirm_bank()
        self.with_context(ctx)._confirm_orders()
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
        }







