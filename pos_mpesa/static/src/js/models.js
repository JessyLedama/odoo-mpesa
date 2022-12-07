function pos_mpesa_models(instance, module){
    var _t = instance.web._t;

    var PaymentlineSuper = module.Paymentline;
    module.Paymentline = module.Paymentline.extend({
        initialize: function(attributes, options) {
            var self = this;
            PaymentlineSuper.prototype.initialize.apply(self, arguments);
            self.mpesa_cashregister = self.cashregister.journal.mpesa_payment_terminal;
            self.phone = null;
            self.payment_status = self.mpesa_cashregister ? 'pending': 'done';
            self._reset_state();
        },
        set_phone: function (phone) {
            // TODO: Add a check/format func on line for the phone
            var self = this;
            self.phone = phone;
        },
        set_payment_status: function(state) {
            var self = this;
            self.payment_status = state;
            if (state === 'done') {
                this.trigger('change:selected', this);
            }
        },
        _reset_state: function () {
            var self = this;
            self.remaining_polls = 3;
        },
        _handle_odoo_connection_failure: function (data) {
            var self = this;
            self.set_payment_status('retry');
            self._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'));
            return Promise.reject(data);
        },
        _poll_for_response: function (resolve, reject) {
            var self = this;
            var MpesaTransaction = new instance.web.Model('mpesa.payment.transaction');
            return MpesaTransaction.call(
                'get_transaction',
                [
                    self.phone,
                    self.amount
                ],
                undefined
            ).then(function (response) {
                // TODO: Status should be a dict with parnter id as well
               self.remaining_polls--;
                
                if (response.status === 'done') {
                    // TODO: Set client here: get order, set client
                    self.set_payment_status('done');
                    resolve(true);
                    self._reset_state();
                } else if (self.remaining_polls <= 0) {
                    self._show_error(_t('Transaction not found on database. Please check details and try again.'));
                    self._reset_state();
                    resolve(false);
                } else {
                    setTimeout(() => {
                        self._poll_for_response(resolve, reject);
                    }, 3000,resolve,reject);
                }
            }).fail(function (data) {
                reject();
                return self._handle_odoo_connection_failure(data);
            });
        },
        confirm_mpesa_payment: function() {
            var self = this;
            if(!self._validate_data())
            {
                return;
            }
            var res = new Promise(function (resolve, reject) {
                self._poll_for_response(resolve, reject);
            });

            res.finally(function () {
                self._reset_state();
            });

            return res;
        },
        _validate_data: function() {
            var self = this;
            if(!self.phone)
            {
                self._show_error(_t('Please enter a phone number'));
                return false;
            }
            if(!self.amount)
            {
                self._show_error(_t('Please enter an amount'));
                return false;
            }
            return true
        },
        _show_error: function (msg, title) {
            var self = this;
            if (!title) {
                title =  _t('MPesa Error');
            }
            self.pos.pos_widget.screen_selector.show_popup('error',{
                message: title,
                comment: msg,
            });
        },
    });
};

    