# -*- coding: utf-8 -*-
import logging 
from datetime import datetime 

from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)

class PosMpesaController(http.Controller):
    _mpesa_tx_url = '/payment/mpesa/callback/'

    @http.route(
        ['/payment/mpesa/callback/'], type='json', auth='none', methods=['POST'], 
        csrf=False, website=True)
    def mpesa_return(self, **post):
        # post signature
        #         {
        #     "TransactionType":"",
        #     "TransID":"LGR219G3EY",
        #     "TransTime":"20170727104247",
        #     "TransAmount":"10.00",
        #     "BusinessShortCode":"600134",
        #     "BillRefNumber":"xyz",
        #     "InvoiceNumber":"",
        #     "OrgAccountBalance":"49197.00",
        #     "ThirdPartyTransID":"1234567890",
        #     "MSISDN":"254708374149",
        #     "FirstName":"John",
        #     "MiddleName":"",
        #     "LastName":""
        #   }
        # TODO: If post empty, say no. If items missing, tell them 
        name = post.get('FirstName', '') + ' ' + post.get('MiddleName', '') + ' ' + post.get('LastName', '')
        request.env['mpesa.payment.transaction'].sudo().create({
            'name': post.get('BillRefNumber'),
            'customer_name': name,
            'amount': post.get('TransAmount'),
            'phone_number': post.get('MSISDN'),
            'reference': post.get('InvoiceNumber'),
            # 'payment_date': datetime.fromtimestamp(post.get('TransTime')),
            # 'state': post.get(), # Not too sure how to handle this as yet
        })