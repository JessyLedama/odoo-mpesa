# -*- coding: utf-8 -*-

import base64
import logging
import requests
import datetime

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    mpesa_reference = fields.Char('Mpesa Reference')
    phone = fields.Char("Mobile Num.")

    @api.model
    def _mpesa_form_get_tx_from_data(self, data):
        reference = data['reference']
        payment_tx = self.search([('reference', '=', reference)])
        if not payment_tx or len(payment_tx) > 1:
            error_msg = _(
                'Mpesa: Received data for reference %s') % reference
            if not payment_tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return payment_tx

    @api.model
    def _mpesa_form_validate(self, transaction, data):
        data = {
            'acquirer_reference': data['txn_id'],
            'state': data['state'],
            'phone': data['phone'],
            'mpesa_reference': data['mpesa_code'],
        }
        transaction.write(data)
