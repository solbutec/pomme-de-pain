# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint

class AccountBankStatine(models.Model):
	_inherit = 'account.bank.statement.line'

	pos_vendeur_id = fields.Many2one("res.users", string='Vendeur', related='pos_statement_id.user_id', store=True) 


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def main_courant_rapport(self):
    	context = self._context or {}
    	pos_company_id = context.get('pos_company_id', False)
    	pos_config_id = context.get('pos_config_id', False)
    	date_start_report = context.get('date_start_report', False)
    	date_end_report = context.get('date_end_report', False)
    	type_reporting = context.get('type_reporting', False)
    	user_reporting = context.get('user_reporting', False)
    	lines = []
    	if pos_company_id and pos_config_id and date_start_report and date_end_report:
    		if type_reporting == 'main_ouvre_cais' and user_reporting:
    			py_lines = self.sudo().env['account.bank.statement.line'].read_group(domain=[
    				('company_id', '=', pos_company_id),
    				('config_id', '=', pos_config_id),
    				('date', '>=', date_start_report),
    				('date', '<=', date_end_report),
    				('pos_vendeur_id', '=', int(user_reporting or 0))
    				],fields=['amount_currency', 'amount'], groupby=['journal_id'])
    			for line in py_lines:
    				lines.append({
    					'type': 'normal',
    					'name': self.sudo().env['account.journal'].browse(line['journal_id'][0]).name,
    					'total': line['amount'],
    					})

    		elif type_reporting == 'main_ouvre_glob':
    			py_lines = self.sudo().env['account.bank.statement.line'].read_group(domain=[
    				('company_id', '=', pos_company_id),
    				('config_id', '=', pos_config_id),
    				('date', '>=', date_start_report),
    				('date', '<=', date_end_report)
    				],fields=['amount_currency','amount'], groupby=['journal_id'])
    			for line in py_lines:
    				lines.append({
    					'type': 'normal',
    					'name': self.sudo().env['account.journal'].browse(line['journal_id'][0]).name,
    					'total': line['amount'],
    					})
    	print(context, "----", lines)
    	return lines 



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
