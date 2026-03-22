# -*- coding: utf-8 -*-
# from odoo import http


# class VentasCustom(http.Controller):
#     @http.route('/ventas_custom/ventas_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ventas_custom/ventas_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ventas_custom.listing', {
#             'root': '/ventas_custom/ventas_custom',
#             'objects': http.request.env['ventas_custom.ventas_custom'].search([]),
#         })

#     @http.route('/ventas_custom/ventas_custom/objects/<model("ventas_custom.ventas_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ventas_custom.object', {
#             'object': obj
#         })

