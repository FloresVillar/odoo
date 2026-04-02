# -*- coding: utf-8 -*-
# from odoo import http


# class Proveedores(http.Controller):
#     @http.route('/proveedores/proveedores', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/proveedores/proveedores/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('proveedores.listing', {
#             'root': '/proveedores/proveedores',
#             'objects': http.request.env['proveedores.proveedores'].search([]),
#         })

#     @http.route('/proveedores/proveedores/objects/<model("proveedores.proveedores"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('proveedores.object', {
#             'object': obj
#         })

