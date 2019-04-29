from odoo import fields, models, api, tools, _
from functools import partial
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

class AccountBankStatementLineReporting(models.Model):
    _name = "kzm.account.bank.statement.line.reporting"
    _auto = False

    r_session_id = fields.Many2one('pos.session', string="Session", readonly=True)
    r_config_id = fields.Many2one('pos.config', string="Config", readonly=True)
    amount_change = fields.Float(string='Amount in', readonly=True)
    amount_due = fields.Float(string='Amount out', readonly=True)
    r_date = fields.Date(string='Date', readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, '%s' % self._table)
        self._cr.execute(""" 
        CREATE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY ac.id, absl1.date ) AS id,
                     ac.id as currency_id,
                     sum(CASE WHEN absl1.change_currency = ac.id THEN absl1.amount_change
                     ELSE 0
                     END) as amount_change,
                     sum(CASE WHEN absl1.due_currency = ac.id THEN absl1.amount_due
                     ELSE 0
                     END) as amount_due,
                     absl1.date as r_date,
                     absl1.session_id as r_session_id,
                     absl1.config_id as r_config_id
                FROM res_currency ac
                    LEFT JOIN account_bank_statement_line  absl1 ON absl1.change_currency = ac.id or absl1.due_currency = ac.id
                where 
                     ac.active = true
                GROUP BY
                    ac.id, r_session_id, r_config_id, r_date
                ORDER BY
                    r_date desc


            )""" % (self._table))
