# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Venta(models.Model):
    _name = 'ventas.venta'
    _description = 'registro de ventas'

    name = fields.Char(String='Codigo',required=True)
    cliente_id = fields.Many2one()     # muchas ventas por un solo cliente
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

