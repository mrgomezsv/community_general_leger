# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountGroup(models.Model):
    _inherit = 'account.group'

    major_account = fields.Boolean(string="Es cuenta de mayor?")