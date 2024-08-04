# -*- coding: utf-8 -*-
from odoo import api, fields, models

class GeneralLedger(models.TransientModel):
    _name = 'general.ledger'
    _description = 'General Ledger'

    # Definición de campos para el modelo
    report_from_date = fields.Date(string="Reporte desde", required=True, default=fields.Date.context_today)
    report_to_date = fields.Date(string="Reporte hasta", required=True, default=fields.Date.context_today)
    categ_ids = fields.Many2many('product.category', string="Categoria de los productos")
    # res_seller_ids = fields.Many2many('account.analytic.account', string="Cuentas Analíticas", required=True)
    # company_id = fields.Many2one(comodel_name="res.company", string="Compañia", required=True, default=lambda self: self.env.company.id)
    file_content = fields.Binary(string="Archivo Contenido")

    def action_generate_excel(self):
        # Este método no hace nada
        pass
