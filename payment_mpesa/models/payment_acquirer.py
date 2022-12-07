# -*- coding: utf-8 -*-

from openerp import api, models, fields


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    shortcode = fields.Char("Short Code", required_if_provider='mpesa')
    request_url = fields.Char("Request URL", required_if_provider='mpesa')
    callback_url = fields.Char("CallBack URL", required_if_provider='mpesa')
    max_amount = fields.Float("Max. Amount", default='150000', required_if_provider='mpesa')

    @api.model
    def _get_providers(self):
        providers = super(PaymentAcquirer, self)._get_providers()
        providers.append(['mpesa', 'M-pesa'])
        return providers

    @api.multi
    def mpesa_get_form_action_url(self):
        self.ensure_one()
        return '/shop/payment/validate'
