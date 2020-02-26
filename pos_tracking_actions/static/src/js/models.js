odoo.define('pos_tracking_actions.models', function(require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var _t = core._t;
    var PosModelSuper = models.PosModel;
    var OrderlineSuper = models.Orderline;

    // var models_pos = models.PosModel.prototype.models;
    // for (var i = 0; i < models_pos.length; i++) {
    //     var model = models_pos[i];
    //     if (model.model === 'pos.order') {
    //         model.fields.push('pos_history_operations');
            
    //     }
    // }
    models.load_fields("pos.order", ['pos_history_operations',]);

    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity){

            var res = OrderlineSuper.prototype.set_quantity.call(this, quantity);
            //message_forme = "user manager /}{/ opération (annulation, modfication, suppression) /}{/ description (voir haut) "

            var self = this;
            var order = self.pos.get_order();
            console.log(quantity,"SOL:", self);
            var user = self.pos.get_cashier();
            if (quantity == 'remove') {
               // order.pos_history_operations += user.name" /}{/ suppression /}{/ ligne de commande '"+self.product.name+"', qty: '"+self.quantity+"' \n"
            }

            return res;
        },
    });

});