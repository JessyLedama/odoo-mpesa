openerp.pos_mpesa = function (instance) {
    var module = instance.point_of_sale;
    pos_mpesa_models(instance, module);
    pos_mpesa_screens(instance, module);
};