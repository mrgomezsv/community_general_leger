# -*- coding: utf-8 -*-
# from odoo import http


# class ModuleSacffold(http.Controller):
#     @http.route('/module_sacffold/module_sacffold', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_sacffold/module_sacffold/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_sacffold.listing', {
#             'root': '/module_sacffold/module_sacffold',
#             'objects': http.request.env['module_sacffold.module_sacffold'].search([]),
#         })

#     @http.route('/module_sacffold/module_sacffold/objects/<model("module_sacffold.module_sacffold"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_sacffold.object', {
#             'object': obj
#         })
