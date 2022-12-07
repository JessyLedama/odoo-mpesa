# -*- coding: utf-8 -*-
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class MpesaPaymentTransactions(models.Model):
    _name = 'mpesa.payment.transaction'

    # TODO: Add default currency search
    # TODO: Create a group for this model

    name = fields.Char(string='Mpesa Ref. No.')
    customer_name = fields.Char(string='Customer Name')
    amount = fields.Float(string='Amount') # Add precision digits
    currency_id = fields.Many2one('res.currency', string='Currency')
    phone_number = fields.Char(string='Phone') # Must have a method to ensure number format
    partner_id = fields.Many2one('res.partner', string='Customer') # compute this field
    reference = fields.Char(string='Origin Reference')
    payment_date = fields.Datetime(string='Date', required=True, readonly=True, default=lambda self: fields.Datetime.now())
    origin = fields.Selection([
        ('ecommerce', 'E-Commerce'),
        ('pos', 'POS'),
        ('sale', 'Sales')
    ], string='Origin', default='pos') # Consider calculating this by checking on the reference in ecomm, sales, etc
                                       # If does not exist is certainly pos ??   
    state = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('reverse', 'Reversed'),
    ], string='Status', default='pending') # Require actions that move these states

    # TODO: Add display_name func: MPESA TX QWER789k09
    # TODO: Add way to relate to relevant accounting record

    @api.model
    def create(self, vals):
        # partner_object = self.env['res.partner']
        # partner = partner_object.sudo().search([('name', 'ilike', vals['customer_name']), ('mobile', 'ilike', vals['phone_number'])], limit=1)
        # if not partner:
        #     partner = partner_object.sudo().create({
        #         'name': vals['customer_name'],
        #         'mobile': vals['phone_number']
        #     })
        # vals['partner_id'] = partner.id
        return super(MpesaPaymentTransactions, self).create(vals)

    @api.model
    def get_transaction(self, phone, amount):
        # TODO: Restrict search with date and time
        # TODO: If not tx, send error data
        # TODO: If tx but not pending, then say it has already been reconciled
        _logger.info('phone %s' % phone)
        _logger.info('amount %s' % amount)
        tx = self.env['mpesa.payment.transaction'].sudo().search([('phone_number', 'ilike', phone), ('amount', '=', amount)], limit=1)
        if tx:
            # state = 'done' # FIXME: How to deal with state here
            # partner_id = tx.partner_id.id
            return {
                'status': 'done',
                'partner_id': None
            }
        else:
            return {
                'error': "No Transaction found. Try again"
            }