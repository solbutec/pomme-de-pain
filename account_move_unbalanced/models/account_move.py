# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env.user.company_id.currency_id.decimal_places

        self._cr.execute("""\
            SELECT      move_id, sum(debit), sum(credit)
            FROM        account_move_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        for res in self._cr.fetchall():
            move_id, debit, credit = res
            diff = debit - credit
            move = self.env['account.move'].browse(move_id)
            if diff <= (10 ** (-prec)):
                last_move_line = [l for l in move.line_ids ]
                last_move_line = last_move_line[-1]
                self._cr.execute("""\
                    UPDATE      account_move_line
                    SET credit =  %s
                    WHERE id = %s
                    """, (l.credit + diff,last_move_line.id))      
        return super(AccountMove, self).assert_balanced()
