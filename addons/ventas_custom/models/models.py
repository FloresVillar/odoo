# -*- coding: utf-8 -*-
from odoo import models, fields, api

#-----------VENTA-------------------------------
class Venta(models.Model):
    _name = 'ventas.venta'
    _description = 'registro de ventas'
    name = fields.Char(String='Codigo',required=True)
    cliente_id = fields.Many2one('res.partner',string="Cliente")     # muchos registros de la tabla actual ←→ un registro de la otra tabla
    #value2 = fields.Float(compute="_value_pc", store=True)
    fecha = fields.Date(string="Fecha")
    #description = fields.Text()
    lineas_ids = fields.One2many('ventas.venta.linea','venta_id',string="Lineas") # un registro de tabla actual ←→ muchos de la otra tabla
    total = fields.Float(string="Total",compute="_compute_total")
    @api.depends('lineas_ids.subtotal')
    def _compute_total(self):
        for venta in self:
            venta.total = sum(linea.subtotal for linea in venta.lineas_ids)
#-----LINEA VENTA------------------------------------------
class VentaLinea(models.Model):
    _name = "ventas.venta.linea"
    _description = "Linea de venta" # cada linea en la boleta de venta
    venta_id = fields.Many2one('ventas.venta',string="Venta")
    producto = fields.Char(string="Producto") 
    precio =  fields.Float(string="Precio")
    cantidad = fields.Integer(String="Cantidad")
    subtotal = fields.Float(string="Subtotal",compute="_compute_subtotal")
    @api.depends('precio','cantidad')
    def _compute_subtotal(self):
        for linea in self:
            linea.subtotal = linea.precio * linea.cantidad

