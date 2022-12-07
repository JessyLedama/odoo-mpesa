$(document).ready(function() {

    function payment_mpesa(){
       var $payment = $("#payment_method");

        $payment.on("click", 'button[id="mpesa"]', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            $('#mpesa').prop("disabled", true).button('loading');
            var acquirer_id = $(ev.currentTarget).parents('div.oe_sale_acquirer_button').first().data('id');
            if (! acquirer_id) {
                return false;
            }
            openerp.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function(){
                console.log("After payment Transaction...");
                mpesa_number = $('#mpesa_number').val();
                if(!mpesa_number){
                    var $phone = $('#right_column').find("span[itemprop=telephone]")
                    if ($phone.length > 0){
                        var mpesa_number = $phone.text();
                        $('#mpesa_number').val(mpesa_number);
                    }
                }
                if(mpesa_number && mpesa_number.length < 10){
                    $('#mpesa-errors').text("M-Pesa Number doesn't look valid!").addClass("alert alert-danger");

                } else {
                    openerp.jsonRpc('/payment/mpesa/charge', 'call', {'phone': mpesa_number}).then(function(response) {
                        console.log("Attempting payment charge.....");
                        if (response === true) {
                            $("#form-mpesa").get(0).submit();
                            console.log("We have made the charge....");
                        } else {
                            console.log("Charge failed.....");
                            $('#mpesa').prop("disabled", false).button('reset');
                            $('#mpesa-errors').text(response).addClass("alert alert-danger");
                        }
                    });
                }

            });
        });
    }

    payment_mpesa();
}); 
