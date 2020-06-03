# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
from pytz import timezone
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.depends('customer_name', 'customer_phone', 'customer_addr')
    def compute_delivr(self):
        for o in self:
            o.delivring_order = (o.customer_name or o.customer_phone or o.customer_addr)

    salesman_id = fields.Many2one('res.users', string='Salesman')
    #init_user_id, c'est le createur, car parfois, quand on change pos user (manger)
    #pour faire des corrections, le systeme passe dans caissier, le modificateur
    init_user_id = fields.Many2one("res.users", string="Initiator")
    customer_name = fields.Char("Delivered name")
    customer_phone = fields.Char("Delivered phone")
    customer_addr = fields.Char("Delivered address")
    delivring_order = fields.Boolean("Deliver order", compute=compute_delivr, store=True)

    def create(self, values):
        # print("Try To CREATE ,,,")
        # from pprint import pprint
        # pprint(values)
        order_id = super(PosOrder, self).create(values)
        if not order_id.user_id.pos_user_type == 'cashier':
            notifications = []
            users = self.env['res.users'].search([])
            for user in users:
                if user.sales_persons:
                    for salesperson in user.sales_persons:
                        if salesperson.id == order_id.user_id.id:
                            session = self.env['pos.session'].search([('user_id', '=', user.id)], limit=1)
                            if session:
                                notifications.append(
                                    [(self._cr.dbname, 'sale.note', user.id), {'new_pos_order': order_id.read()}])
                                self.env['bus.bus'].sendmany(notifications)
        return order_id

    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        from pprint import pprint
        res.update({
            'salesman_id': ui_order.get('salesman_id') or False,
            'init_user_id': ui_order.get('init_user_id') or False,
            'customer_name': ui_order.get('customer_name') or False,
            'customer_phone': ui_order.get('customer_phone') or False,
            'customer_addr': ui_order.get('customer_addr') or False,
        })
        return res

    @api.multi
    def unlink(self):
        for ord in self:
            notifications = []
            notify_users = []
            order_user = self.env['res.users'].browse(ord.user_id.id)
            if ord.salesman_id:
                if self._uid == ord.salesman_id.id:
                    users = self.env['res.users'].search([])
                    for user in users:
                        if user.sales_persons:
                            for salesperson in user.sales_persons:
                                if salesperson.id == ord.user_id.id:
                                    session = self.env['pos.session'].search([('user_id','=',user.id)], limit=1)
                                    if session:
                                        notify_users.append(session.user_id.id)
                else:
                    notify_users.append(ord.salesman_id.id)
                for user in notify_users:
                    notifications.append([(self._cr.dbname, 'sale.note', user),
                                              {'cancelled_sale_note': ord.read()}])
                self.env['bus.bus'].sendmany(notifications)
        return super(PosOrder, self).unlink()

    @api.multi
    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        notifications = []
        notify_users = []
        order_id = self.browse(vals.get('old_order_id'))
        order_user = self.env['res.users'].browse(vals.get('user_id'))
        users = self.env['res.users'].search([])
        for user in users:
            if user.sales_persons:
                if user.id == order_user.id:
                    session = self.env['pos.session'].search([('user_id','=',user.id)], limit=1)
                    if session:
                        notify_users.append(session.user_id.id)

        for user in notify_users:
            notifications.append(((self._cr.dbname, 'sale.note', user),
                                      ('new_pos_order', order_id.read())))
        self.env['bus.bus'].sendmany(notifications)
        return res

    @api.multi
    def action_pos_order_paid(self):
        if not self.test_paid():
            raise UserError(_("Order is not paid."))
        self.write({'state': 'paid'})
        notifications_for_products =[]
        notifications = []
        notify_users = []
        order_id = self
        order_user = self.env['res.users'].browse(order_id.user_id.id)
        if order_id.salesman_id:
            notify_users.append(order_id.salesman_id.id)
        users = self.env['res.users'].search([])
        for user in users:
            if user.sales_persons:
                if user.id == order_user.id:
                    session = self.env['pos.session'].search([('user_id','=',user.id)], limit=1)
                    if session:
                        notify_users.append(session.user_id.id)
        if len(notify_users) > 0:
            for user in notify_users:
                notifications.append([(self._cr.dbname, 'sale.note', user),
                                          {'new_pos_order': order_id.read()}])
            self.env['bus.bus'].sendmany(notifications)
        return self.create_picking()

    @api.model
    def _process_order(self,order):
        pos_line_obj = self.env['pos.order.line']
        draft_order_id = order.get('old_order_id')
        if order.get('draft_order'):
            if not draft_order_id:
                order.pop('draft_order')
                order_id = self.create(self._order_fields(order))
                return order_id
            else:
                order_id = draft_order_id
                pos_line_ids = pos_line_obj.search([('order_id', '=', order_id)])
                if pos_line_ids:
                    pos_line_obj.unlink(pos_line_ids)
                self.write([order_id],
                           {'lines': order['lines'],
                            'partner_id': order.get('partner_id')})
                return order_id

        if not order.get('draft_order') and draft_order_id:
            order_id = draft_order_id
            order_obj = self.browse(order_id)
            pos_line_ids = pos_line_obj.search([('order_id', '=', order_id)])
            if pos_line_ids:
                for line_id in pos_line_ids:
                    line_id.unlink()
            temp = order.copy()
            temp.pop('statement_ids', None)
            temp.pop('name', None)
            temp.update({
                'date_order': order.get('creation_date'),
                'session_id': order.get('pos_session_id'),
            })
            order_obj.write(temp)
            for payments in order['statement_ids']:
                order_obj.add_payment(self._payment_fields(payments[2]))
            session = self.env['pos.session'].browse(order['pos_session_id'])
            if session.sequence_number <= order['sequence_number']:
                session.write({'sequence_number': order['sequence_number'] + 1})
                session.refresh()
            if not float_is_zero(order['amount_return'], self.env['decimal.precision'].precision_get('Account')):
                cash_journal = session.cash_journal_id
                if not cash_journal:
                    cash_journal_ids = session.statement_ids.filtered(lambda st: st.journal_id.type == 'cash')
                    if not len(cash_journal_ids):
                        raise Warning(_('error!'),
                                             _("No cash statement found for this session. Unable to record returned cash."))
                    cash_journal = cash_journal_ids[0].journal_id
                order_obj.add_payment({
                    'amount': -order['amount_return'],
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('return'),
                    'journal': cash_journal.id,
                })
            return order_obj
        if not order.get('draft_order') and not draft_order_id:
            order_id = super(PosOrder, self)._process_order(order)
            return order_id

    @api.model
    def ac_pos_search_read(self, domain):
        domain = domain.get('domain')
        search_vals = self.search_read(domain)
        user_id = self.env['res.users'].browse(self._uid)
        tz = False
        result = []
        if self._context and self._context.get('tz'):
            tz = timezone(self._context.get('tz'))
        elif user_id and user_id.tz:
            tz = timezone(user_id.tz)
        if tz:
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            for val in search_vals:
                date_order = fields.Date.from_string(str(val.get('date_order')))
                date_new_order = datetime.strftime(date_order, DEFAULT_SERVER_DATETIME_FORMAT)
                if sign == '-':
                    val.update({
                        'date_order':(val.get('date_order') - timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                elif sign == '+':
                    val.update({
                        'date_order':(val.get('date_order') + timedelta(hours=hour_tz, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
                    })
                result.append(val)
            return result
        else:
            return search_vals


class pos_config(models.Model):
    _inherit = "pos.config"

    enable_reorder = fields.Boolean("Order Sync")
    enable_operation_restrict = fields.Boolean("Operation Restrict")
    pos_managers_ids = fields.Many2many('res.users','posconfig_partner_rel','location_id','partner_id', string='Managers')

class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_user_type = fields.Selection([('cashier', 'Cashier'), ('salesman', 'Sales Person')],string="POS User Type", default='salesman')
    can_give_discount = fields.Boolean("Can Give Discount")
    can_change_price = fields.Boolean("Can Change Price")
    discount_limit = fields.Float("Discount Limit")
    based_on = fields.Selection([('pin','Pin'),('barcode','Barcode')],
                                   default='barcode',string="Authenticaion Based On")
    sales_persons = fields.Many2many('res.users','sales_person_rel','sales_person_id','user_id', string='Sales Person')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_sales_person'):
            users = []
            pos_users_ids = self.env.ref('point_of_sale.group_pos_user').users.ids
            sale_person_ids = self.search([('id', 'in', pos_users_ids),
                                           ('pos_user_type', '=', 'salesman')])
            selected_sales_persons = []
            for user in pos_users_ids:
                user_id = self.browse(user)
                if user_id.sales_persons:
                    selected_sales_persons.append(user_id.sales_persons.ids)
            if sale_person_ids:
                users.append(sale_person_ids.ids)
            if users:
                args += [['id', 'in', users[0]]]
            if selected_sales_persons:
                args += [['id', 'not in', selected_sales_persons[0]]]
        return super(ResUsers, self).name_search(name, args=args, operator=operator, limit=limit)


class PosTable(models.Model):
    _inherit = 'restaurant.table'

    is_for_delivery = fields.Boolean("Is for delivery", default=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: