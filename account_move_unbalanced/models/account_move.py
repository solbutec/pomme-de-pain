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
        print(self._cr.fetchall())
        for m in self:
            print("---- MOVE ", m.id)
            for l in m.line_ids:
                print("LI", l.id, l.name, l.debit, l.credit)
        # if len(self._cr.fetchall()) != 0:
        #     raise UserError(_("Cannot create unbalanced journal entry."))
        return super(AccountMove, self).assert_balanced()
