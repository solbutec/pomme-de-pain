# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint

class AccountBankStatine(models.Model):
    _inherit = 'account.bank.statement.line'

    pos_vendeur_id = fields.Many2one("res.users", string='Vendeur', related='pos_statement_id.user_id', store=True) 

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    config_id = fields.Many2one("pos.config", string="Pos config", related='order_id.config_id', store=True)
    pos_vendeur_id = fields.Many2one("res.users", string='Vendeur', related='order_id.user_id', store=True) 
    product_categ_id = fields.Many2one("product.category", string="Categ article", related='product_id.categ_id', store=True)
    pos_categ_id = fields.Many2one("pos.category", string="Pos categorie", related='product_id.pos_categ_id', store=True)



class PosConfig(models.Model):
    _inherit = 'pos.config'

    def open_wizard_reporting(self):
        action = self.env.ref('pdp_reporting.action_view_pdp_pos_reporting_wizard').read()[0]
        action['context'] = {'default_pos_config': self.id}
        return action

    @api.model
    def main_courant_rapport(self):
        context = self._context or {}
        pos_company_id = context.get('pos_company_id', False)
        pos_config_id = context.get('pos_config_id', False)
        date_start_report = context.get('date_start_report', False)
        date_end_report = context.get('date_end_report', False)
        type_reporting = context.get('type_reporting', False)
        user_reporting = context.get('user_reporting', False)
        pricelist_id = context.get('pricelist_id', False)
        pricelist_id = pricelist_id if (pricelist_id and (pricelist_id!= -1)) else False
        pricelist_id = pricelist_id and self.sudo().env['product.pricelist'].browse(pricelist_id) or False
        lines = []
        if pos_company_id and pos_config_id and date_start_report and date_end_report:
            
            if type_reporting == 'main_ouvre_cais' and user_reporting:
                py_lines = self.sudo().env['account.bank.statement.line'].read_group(domain=[
                    ('company_id', '=', pos_company_id),
                    ('config_id', '=', pos_config_id),
                    ('date', '>=', date_start_report),
                    ('date', '<=', date_end_report),
                    ('pos_vendeur_id', '=', int(user_reporting or 0)),
                    ],fields=['amount_currency', 'amount'], groupby=['journal_id'])
                tot = 0
                for line in py_lines:
                    lines.append({
                        'type': 'normal',
                        'name': self.sudo().env['account.journal'].browse(line['journal_id'][0]).name,
                        'total': line['amount'],
                        })
                    tot += line['amount']
                if len(lines):
                    lines.append({
                        'type': 'total_method',
                        'total': tot,
                        })

            elif type_reporting == 'main_ouvre_glob':
                py_lines = self.sudo().env['account.bank.statement.line'].read_group(domain=[
                    ('company_id', '=', pos_company_id),
                    ('config_id', '=', pos_config_id),
                    ('date', '>=', date_start_report),
                    ('date', '<=', date_end_report),
                    ],fields=['amount_currency','amount'], groupby=['journal_id'])
                tot = 0
                for line in py_lines:
                    lines.append({
                        'type': 'normal',
                        'name': self.sudo().env['account.journal'].browse(line['journal_id'][0]).name,
                        'total': line['amount'],
                        })
                    tot += line['amount']
                if len(lines):
                    lines.append({
                        'type': 'total_method',
                        'total': tot,
                        })

            elif type_reporting in ['vente_eclat', 'vente_non_eclat']:
                my_demain = [
                    ('company_id', '=', pos_company_id),
                    ('config_id', '=', pos_config_id),
                    ('create_date', '>=', date_start_report),
                    ('create_date', '<=', date_end_report),
                    ('is_combo', '=', False),
                    ]
                if type_reporting == 'vente_non_eclat':
                    my_demain = my_demain[:-1]
                    my_demain += [('is_splmnt', '=', False)]
                # Try to do date + price unit menu = (amount total lines / qty)
                py_lines = self.sudo().env['pos.order.line'].read_group(domain=my_demain,fields=['price_unit','qty'], groupby=['pos_categ_id', 'product_id'], lazy=False)
                categ_id, categ_qty, total_price = -1, 0, 0
                for line in py_lines:
                    product = self.sudo().env['product.product'].browse(line['product_id'][0])
                    pos_categ_id = line['pos_categ_id'] and line['pos_categ_id'][0] or False
                    pos_categ_id = pos_categ_id and self.sudo().env['pos.category'].browse(line['pos_categ_id'][0])
                    price_unit = product.list_price
                    price_unit = (line['price_unit'] / line['__count']) if (line['__count'] > 0) else 0 #price by pricelist c'est pas line price_unit
                    if pricelist_id:
                        price_unit = pricelist_id.get_product_price(product, 1.0, False)
                    #------------
                    if categ_id != (pos_categ_id and pos_categ_id.id or False):
                        if categ_id != -1:
                            #add categ footer
                            old_categ = categ_id and self.sudo().env['pos.category'].browse(categ_id)
                            lines.append({
                                'type': 'categ_footer',
                                'name': old_categ and old_categ.name or '----',
                                'qty': categ_qty,
                                'total': float(total_price),
                            })
                        categ_id = pos_categ_id and pos_categ_id.id or False
                        categ_qty = 0
                        total_price = 0
                    #----- ligne article
                    lines.append({
                            'type': 'normal',
                            'code': product and product.default_code or '---',
                            'name': product and product.name or '---',
                            'qty': line['qty'],
                            'price_unit': float(price_unit),
                            'total': float(line['qty'] * price_unit),
                            })

                
                    categ_qty += line['qty']
                    total_price += line['qty'] * price_unit
                if len(lines):
                    old_categ = categ_id and self.sudo().env['pos.category'].browse(categ_id)
                    lines.append({
                                'type': 'categ_footer',
                                'name': old_categ and old_categ.name or '----',
                                'qty': categ_qty,
                                'total': total_price,
                            })

                        

        return lines 
