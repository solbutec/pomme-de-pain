# -*- coding: utf-8 -*-
from odoo import http

# class PosMyTest(http.Controller):
#     @http.route('/pos_my_test/pos_my_test/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_my_test/pos_my_test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_my_test.listing', {
#             'root': '/pos_my_test/pos_my_test',
#             'objects': http.request.env['pos_my_test.pos_my_test'].search([]),
#         })

#     @http.route('/pos_my_test/pos_my_test/objects/<model("pos_my_test.pos_my_test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_my_test.object', {
#             'object': obj
#         })