odoo.define('pos_tracking_actions.models', function(require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var _t = core._t;    
    var _super_posmodel = models.PosModel.prototype;

    // add new field
    var _super_posorder = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
                // Add field to model
                _super_posorder.initialize.apply(this,arguments);
                //console.log("ARGS:",this.init_user_id,"::::",arguments);
                this.pos_history_operations = "";
                if(this.init_user_id == undefined)
                    this.init_user_id = this.pos.get_cashier().id || false;

                //return this
            },
        add_actions_history: function(text){
            if(!this.pos_history_operations){
                this.pos_history_operations = "";
            }
            this.pos_history_operations += text || "";
        },
        export_as_JSON: function(){
            var json = _super_posorder.export_as_JSON.apply(this,arguments);
            json.pos_history_operations = this.pos_history_operations;
            return json;
        },
        init_from_JSON: function(json){
            _super_posorder.init_from_JSON.apply(this,arguments);
            this.pos_history_operations = json.pos_history_operations || "";
        },
    });

    // treatement
    var _super_orderlinemodel = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity){
            
            //message_forme = "user manager /}{/ opération (annulation, modfication, suppression) /}{/ description (voir haut) "

            var self = this;
            var order = self.pos.get_order();
            var user = self.pos.get_cashier();
            var user_name = user.name;
            var order_line_name = self.get_product().display_name;
            var current_qty = self.get_quantity();
            if (quantity == 'remove') {
               order.add_actions_history(user_name+" /}{/ suppression /}{/ ligne de commande '"+order_line_name+"' \n");
            }else{
                var quant = parseFloat(quantity) || 0;
                if(quant && quant != 0){
                    if(quant < 0){
                    order.add_actions_history(user_name+" /}{/ modification négative /}{/ ligne de commande '"+order_line_name+"', qty: '"+(current_qty || '0')+"' => '"+(quant || '0')+"' \n");
                   }else{
                    order.add_actions_history(user_name+" /}{/ modification positive /}{/ ligne de commande '"+order_line_name+"', qty: '"+(current_qty || '0')+"' => '"+(quant || '0')+"' \n");
                   }
                }else{
                    order.add_actions_history(user_name+" /}{/ modification nulle /}{/ ligne de commande '"+order_line_name+"', qty: '"+(current_qty || '0')+"' => '"+(quant || '0')+"' \n");
                }
            }
            //order.get_selected_orderline().set_combo_prod_info(order.get_selected_orderline().combo_prod_info);
            this.recompute_unit_price();
            return _super_orderlinemodel.set_quantity.call(this, quantity);//(this, quantity);
            //return res;
        },
        recompute_unit_price: function(){
            //console.log("----------- COMPUTE PRICE ------");
            if(this.combo_prod_info && this.combo_prod_info.length > 0){
                var supp_price = this.product.list_price;
                //console.log("--- init:",supp_price,this)
                for(var i=0; i< this.combo_prod_info.length; i++){
                    supp_price += this.combo_prod_info[i].product_detail.price_supplement;
                }
                 this.set_unit_price(supp_price);
                 this.price = supp_price;
                 //console.log("--- tot:",supp_price,this);
            }
            //console.log("--------------------------------");
            
        },
    });

});