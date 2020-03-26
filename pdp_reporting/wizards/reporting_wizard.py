# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from itertools import groupby

from pprint import pprint

REPORT_TITLES = {
    'main_ouvre_glob': "Main courante global", 
    'main_ouvre_cais': "Main courante (Caissier)", 
    'vente_eclat': "Ventes éclatées",
    'vente_non_eclat': "Ventes non éclatées",
    'rapport_des_traces': "Rapport des traces",
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
        ('vente_non_eclat', "Ventes non éclatées"),
        ('rapport_des_traces', "Rapport des traces")],
                            default='main_ouvre_glob')
    cashier_id = fields.Many2one('res.users', string="Cashier")
    pos_config_id = fields.Many2one("pos.config", string="Pos config", default= get_pos_config)

    @api.multi
    def action_print(self):
        rapport = self.sudo().env.ref('pdp_reporting.report_main_courante')
        return rapport.report_action(self)

    def get_data_reporting(self):
        lines_report = []
        if self.type in ['main_ouvre_glob', 'main_ouvre_cais']:
            my_domaine = [
                    ('config_id', '=', self.sudo().pos_config_id.id),
                    ('create_date', '>=', self.debut_date),
                    ('create_date', '<=', self.end_date),
                    ]
            if self.type == 'main_ouvre_cais':
                my_domaine.append(('pos_vendeur_id', '=', self.sudo().cashier_id.id))
            py_lines = self.sudo().env['account.bank.statement.line'].search(my_domaine)
            tot = 0
            for journal_id, lines_jrn in groupby(py_lines, lambda l: l.sudo().journal_id):
                lines_jrn = list(lines_jrn)
                for pos_order, lines in groupby(lines_jrn, lambda l: l.sudo().pos_statement_id):
                    lines = list(lines)
                    detail = ""
                    lines_report.append({
                        'type': 'normal',
                        'name': pos_order.sudo().name,
                        'cashier': pos_order.sudo().user_id.name,
                        'total': sum([l.sudo().amount for l in lines]),
                        'detail': "<br/>".join([("&#160;&#160;&#160;&#160;*" if l.sudo().is_splmnt else " ")+str(l.sudo().qty)+" "+str(l.sudo().product_id.name) for l in pos_order.lines]),
                        })
                tot_line = sum([l.sudo().amount for l in lines_jrn])
                lines_report.append({
                    'type': 'method',
                    'name': journal_id.sudo().name,
                    'total': tot_line,
                })
                tot += tot_line
            
            if len(lines_report):
                lines_report.append({
                    'type': 'total',
                     'total': tot,
                    })
        if self.type in ['vente_eclat', 'vente_non_eclat']:
            new_context = {
             'pos_config_id': self.sudo().pos_config_id.id,
             'pos_company_id': self.sudo().env.user.company_id.id,
             'date_start_report': self.debut_date,
             'date_end_report': self.end_date,
             'type_reporting': self.type,
             'user_reporting': self.sudo().cashier_id and self.sudo().cashier_id.id or False,
             'pricelist_id': self.sudo().pos_config_id.pricelist_id.id,
            }
            result = self.pos_config_id.with_context(**new_context).main_courant_rapport()
            if len(result):
                lines_report = result
                result.append({
                    'type': 'total',
                    'total_qty': sum([l['qty'] for l in result if l['type']=='categ_footer']),
                })
        if self.type == 'rapport_des_traces':
            my_domaine = [
                ('config_id', '=', self.sudo().pos_config_id.id),
                ('create_date', '>=', self.debut_date),
                ('create_date', '<=', self.end_date),
            ]
            py_lines = self.sudo().env['pos.order'].search(my_domaine)
            filtred_lines = py_lines and py_lines.filtered(lambda r: r.pos_history_operations and ('modification nulle' in r.pos_history_operations or
                                                       'modification négative' in r.pos_history_operations or
                                                       'suppression' in r.pos_history_operations)) or []
            for pos_order in filtred_lines:
                show_lines = []
                text_lines = pos_order.sudo().pos_history_operations and pos_order.sudo().pos_history_operations.split('\n') or []
                for line in text_lines:
                    if 'modification nulle' in line or 'modification négative' in line or 'suppression' in line:
                        show_lines.append((", ".join(line.strip().split(' /}{/ '))).strip())
                lines_report.append({
                    'type': 'rapport_des_traces',
                    'date_order': pos_order.sudo().date_order,
                    'name': pos_order.sudo().name,
                    'pos_history_operations': "<br/>".join(show_lines),
                })
        return lines_report

