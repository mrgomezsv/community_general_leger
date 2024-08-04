# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountGroup(models.Model):
    _inherit = 'account.group'

    company_id = fields.Many2one('res.company', string="Compañia", default=lambda self: self.env.company)
    major_account = fields.Boolean(string="Es cuenta de mayor?")
