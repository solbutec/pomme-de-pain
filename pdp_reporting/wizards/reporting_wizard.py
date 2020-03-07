# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from pprint import pprint

REPORT_TITLES = {
    'main_ouvre_glob': "Main courante global", 
    'main_ouvre_cais': "Main courante (Caissier)", 
    'vente_eclat': "Ventes éclatées",
    'vente_non_eclat': "Ventes non éclatées",
}
class PosConfigWizard(models.TransientModel):
    _name = 'pos.config.reporting.wizard'

    def get_pos_config(self):
        context = self._context or {}
        return context.get('default_pos_config', False)

    def get_start_date(self):
        date_start = fields.Datetime.now().replace(hour=7, minute=0, second=0)

        return date_start

    def get_report_title(self):
        return REPORT_TITLES[self.type] if self.type else '-'


    debut_date = fields.Datetime("Du", default=get_start_date)
    end_date = fields.Datetime("Au", default=fields.Datetime.now)
    type = fields.Selection([
        ('main_ouvre_glob', "Main courante global"), 
        ('main_ouvre_cais', "Main courante (Caissier)"), 
        ('vente_eclat', "Ventes éclatées"),
        ('vente_non_eclat', "Ventes non éclatées")],
                            default='main_ouvre_glob')
    cashier_id = fields.Many2one('res.users', string="Cashier")
    pos_config_id = fields.Many2one("pos.config", string="Pos config", default= get_pos_config)

    @api.multi
    def action_print(self):
        rapport = self.sudo().env.ref('pdp_reporting.report_main_courante')

        # lines getted on report qweb by get_data_reporting method
        if self.type in ['main_ouvre_glob', 'main_ouvre_cais']:
            my_domaine = [
                    ('config_id', '=', self.pos_config_id.id),
                    ('date', '>=', self.debut_date),
                    ('date', '<=', self.end_date),
                    ]
            if self.type == 'main_ouvre_cais':
                my_domaine.append(('pos_vendeur_id', '=', self.cashier_id.id))
            py_lines = self.sudo().env['account.bank.statement.line'].read_group(domain=my_domaine,
                fields=['amount_currency', 'amount'], groupby=['journal_id'])

            return rapport.report_action(self)

        elif self.type == 'vente_eclat':
            pass
        elif self.type == 'vente_non_eclat':
            pass

    def get_data_reporting(slef):
        return []

