# -*- coding: utf-8 -*-
from odoo import http

# class BpNeracaSaldoPdam(http.Controller):
#     @http.route('/bp_neraca_saldo_pdam/bp_neraca_saldo_pdam/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bp_neraca_saldo_pdam/bp_neraca_saldo_pdam/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bp_neraca_saldo_pdam.listing', {
#             'root': '/bp_neraca_saldo_pdam/bp_neraca_saldo_pdam',
#             'objects': http.request.env['bp_neraca_saldo_pdam.bp_neraca_saldo_pdam'].search([]),
#         })

#     @http.route('/bp_neraca_saldo_pdam/bp_neraca_saldo_pdam/objects/<model("bp_neraca_saldo_pdam.bp_neraca_saldo_pdam"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bp_neraca_saldo_pdam.object', {
#             'object': obj
#         })