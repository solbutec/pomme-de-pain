from odoo import fields, models, api, tools, _
from functools import partial
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class PosAccount(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.depends('amount_change', 'amount_due', 'due_currency', 'change_currency')
    def compute_amounts_currencies(self):
        for o in self:
            o.amount_change_curr = o.amount_change
            o.amount_due_curr = o.amount_due

    amount_change = fields.Float("Amount change")
    amount_due = fields.Float("Amount due")
    change_currency = fields.Many2one('res.currency', "change currency")
    due_currency = fields.Many2one('res.currency', "due currency")
    amount_change_curr = fields.Monetary("Amount change", currency_field='change_currency',
                                         compute=compute_amounts_currencies)
    amount_due_curr = fields.Monetary("Amount due", currency_field='due_currency', compute=compute_amounts_currencies)
    session_id = fields.Many2one('pos.session', string="Session", related='pos_statement_id.session_id', store=True)
    config_id = fields.Many2one('pos.config', string="Config", related='pos_statement_id.config_id', store=True)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # @api.model
    # def create(self, vals):
    #     line = super(PosOrder, self).create(vals)
    #     line.compute_amounts_currencies()
    #     return line

    def _payment_fields(self, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(ui_paymentline)
        res.update({
            'amount_change': ui_paymentline['amount_change'],
            'amount_due': ui_paymentline['amount_due'],
            'change_currency': ui_paymentline['change_currency'],
            'due_currency': ui_paymentline['due_currency'],
        })

        return res

    @api.model
    def _process_order(self, pos_order):
        # res = super(PosOrder, self)._process_order(pos_order)
        pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            pos_order['pos_session_id'] = self._get_valid_session(pos_order).id
        order = self.create(self._order_fields(pos_order))
        prec_acc = order.pricelist_id.currency_id.decimal_places
        journal_ids = set()
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                #print("ORDER ADD PAY?NT ::", self._payment_fields(payments[2]))
                order.add_payment(self._payment_fields(payments[2]))
            journal_ids.add(payments[2]['journal_id'])

        if pos_session.sequence_number <= pos_order['sequence_number']:
            pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})
            pos_session.refresh()

        if not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_journal_id = pos_session.cash_journal_id.id
            if not cash_journal_id:
                # Select for change one of the cash journals used in this
                # payment
                cash_journal = self.env['account.journal'].search([
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1)
                if not cash_journal:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal = [statement.journal_id for statement in pos_session.statement_ids if
                                    statement.journal_id.type == 'cash']
                    if not cash_journal:
                        raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                cash_journal_id = cash_journal[0].id
            order.add_payment({
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_name': _('return'),
                'journal': cash_journal_id,
                'amount_change': 0,
                'amount_due': 0,
                'change_currency': False,
                'due_currency': False,
            })
        return order

    def _prepare_bank_statement_line_payment_values(self, data):
        """Create a new payment for the order"""
        args = super(PosOrder, self)._prepare_bank_statement_line_payment_values(data) or {}
        args.update({
            'amount_change': data.get('amount_change', 0),
            'amount_due': data.get('amount_due', 0),
            'change_currency': data.get('change_currency', False),
            'due_currency': data.get('due_currency', False),
        })
        return args




