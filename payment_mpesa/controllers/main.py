# -*- coding: utf-8 -*-
import json
import yaml
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from openerp import http, _
from openerp.http import request

MAX_RETRIES = 2
BACKOFF_FACTOR = 5
STATUS_FORCELIST = [500, 502, 503, 504]


def create_retry_session():
    """for requests.get() with retry."""
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=STATUS_FORCELIST,
    )
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s


class MpesaController(http.Controller):
    _CALLBACK_RECEIVED = False
    _CALLBACK_RESPONSE = {}
    """
        Create a global variable: _callback_received
        Create a function with while loop, waiting for this response, if received, proceed to mpesa_validate_data()
        TODO: _callback_response should be a List of responses, in-case of multiple transactions at the same time
    """

    def _awaiting_mpesa_callback(self, params):
        _retries = 0
        while not self._CALLBACK_RECEIVED and _retries < 5000000:
            _retries += 1
            print("Retrying..................................%s TIMES" % _retries)
            continue

        # We have waited and didn't receive any response, assume transaction failed
        if not self._CALLBACK_RECEIVED:
            return "Error: We were unable to receive your payments. Try again!"

        # Proceeding.....We have received a callbackconfirmation from Mpesa
        _ref = params['reference_id']
        res = self._CALLBACK_RESPONSE

        res['reference'] = _ref  # TODO: Remove

        _ref_from_mpesa = res.get('reference')
        if _ref_from_mpesa and _ref_from_mpesa == _ref:
            # FIXME: Tesfa side: Failed transactions, delayed transactions etc
            self.mpesa_validate_data(res)
            # FIXME: Assume the transaction is successfully
            return True
        else:
            return "We Could not Confirm your Transaction. Try again."

    def create_params(self, acquirer):
        so_id = request.session['sale_order_id']
        so = request.env['sale.order'].sudo().search([('id', '=', so_id)])
        params = {}
        params['description'] = _('%s Order %s' % (so.company_id.name, so.name))
        params['amount'] = int(so.amount_total)
        params['currency'] = so.currency_id.name
        params['reference_id'] = so.name
        params['name'] = so.partner_id.name
        params['phone'] = so.partner_id.phone
        params['email'] = so.partner_id.email
        return params

    def sanitize_phone_number(self, phone):
        if phone and phone.startswith('0'):
            # sanitize phone number
            phone = '254' + phone[1:]
        if phone and phone.startswith('+254'):
            phone = phone[1:]
        return phone

    def mpesa_validate_data(self, data):
        res = False
        tx_obj = request.env['payment.transaction']
        res = tx_obj.sudo().form_feedback(data, 'mpesa')
        print(".................Form Feedback Received...............")
        return res

    @http.route('/payment/mpesa/charge', type='json', auth='public', website=True)
    def charge_mpesa_create(self, **kwargs):
        payment_acquirer = request.env['payment.acquirer']
        mpesa_acq = payment_acquirer.sudo().search(
            [('provider', '=', 'mpesa')])
        params = self.create_params('mpesa')
        phone = params['phone']
        if kwargs.get('phone'):
            phone = kwargs.get('phone')
        try:
            phone = self.sanitize_phone_number(phone)
            request_url = mpesa_acq.request_url
            reference = params['reference_id']
            amount = 1
            if mpesa_acq.environment == 'prod':
                amount = params.get('amount')
            vals = {
                'phone': phone,
                'amount': amount,
                'uiid': reference,
            }
            # Send Request to M-pesa
            response = requests.post(request_url, json=vals)
            if response.status_code == 200:
                # TODO: response is 200 when invalid phone number is entered
                # res = response.json()
                # TODO: STK Push send successfully, wait for mpesa response
                time.sleep(20)    # Give user a few seconds to confirm the tx.
                # return self._awaiting_mpesa_callback(params)
            # TODO: Implement error codes: https://developer.safaricom.co.ke/docs#errors
            else:
                return "M-Pesa api Not Found!"

        except requests.exceptions.ConnectionError as e:
            return "Connection to M-Pesa Could not be established. Try again!"
        except requests.exceptions.Timeout as e:
            return "Connection Timeout. Try again!"

        # After sending response, query api_end_point for the results
        res = self._query_transaction_status(reference, mpesa_acq)
        if res.get('error'):
            return res.get('error')
        self.mpesa_validate_data(res)
        return True

    def _query_transaction_status(self, reference, acquirer):
        s = create_retry_session()
        data = {
            'bill_ref': reference,
        }

        _retries = 0
        _results_received = False
        results = {}
        while not _results_received and _retries < 4:
            _retries += 1
            print("--------------------------MAKING THE CALL REQUEST---------------------------")
            callback_url = acquirer.callback_url
            res = s.get(callback_url, json=data, timeout=10)

            if res.status_code == 200:
                print("Results: %s..............." % res.json())
                _json_res = res.json()
                if _json_res.get('bill_ref'):
                    _results_received = True
                    results.update({
                        'txn_id': request.env['payment.transaction'].search([('reference', '=', reference)]).id,
                        'reference': reference,
                        'state': 'done',
                        'amount': _json_res['trasnction_amount'],
                        'mpesa_code': _json_res['transaction_id'],
                        'phone': _json_res['msisdn']
                    })
                else:
                    time.sleep(10)  # Pause before retrying

            print("Retrying..................................%s TIMES" % _retries)
            continue

        if not _results_received:
            return {'error': "Error: We were unable to process your payment. Try again!"}

        return results

    @http.route('/payment/mpesa/disabled-for-now', type='http', auth="none", methods=["POST", "GET"])
    def mpesa_back(self, **post):
        """
            ConfirmationCallBack from mpesa
            For Now call_back means transaction has been successful
        """
        res = post['params']
        json.loads(res)
        post = yaml.safe_load(res)

        print("Results: %s" % post)

        res = {}
        if post.get('BillRefNumber', False):
            reference = post['BillRefNumber']
            res.update({
                'txn_id': request.env['payment.transaction'].search([('reference', '=', reference)]).id,
                'state': 'done',
                'reference': reference,
                'amount': post['TransAmount'],
                'mpesa_code': post['TransID'],
                'phone': post['MSISDN']
            })
            self._CALLBACK_RECEIVED = True
            self._CALLBACK_RESPONSE = res
            # TODO: create a model to store all the received callbacks
        else:
            return "Transaction status unknown"
