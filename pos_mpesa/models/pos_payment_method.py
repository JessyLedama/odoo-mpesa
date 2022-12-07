# -*- coding: utf-8 -*-

from openerp import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    mpesa_payment_terminal = fields.Boolean(string='Use Mpesa Payment Terminal', default=False)