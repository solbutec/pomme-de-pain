# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosSession(models.Model):
    _inherit = "pos.session"

    closed_by = fields.Many2one('res.users', string='Closed by')

    def write(self, values):
    	if values.get('state', False):
    		if values.get('state') == 'closed':
    			values.update(closed_by=self.env.user.id)
    	return super(PosSession, self).write(values)