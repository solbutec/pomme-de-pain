odoo.define('pos_user_control.models', function (require) {
    "use strict";
    var pos_models = require('point_of_sale.models');
    var aspl_models = require('aspl_pos_order_sync.pos');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var chrome_pos = require('point_of_sale.chrome');

    var models = pos_models.PosModel.prototype.models;

    for (var i = 0; i < models.length; i++) {
        var model = models[i];
        if (model.model === 'res.users') {
            model.fields.push('has_pos_price_control');
            model.fields.push('has_pos_qty_control');
            model.fields.push('has_pos_discount_control');
            model.fields.push('has_pos_back_backspace_control');
            model.fields.push('has_pos_delete_order_control');
            
        }
    }

    screens.NumpadWidget.include({

        init: function (parent, options) {
            this._super(parent, options);
            this.applyAccessRights();
        },

        applyAccessRights: function () {
            this._super();
            var user = this.pos.get_cashier();
            if(user != undefined){
                var has_pos_price_control = user.has_pos_price_control;
                var has_pos_qty_control = user.has_pos_qty_control;
                var has_pos_discount_control = user.has_pos_discount_control;
                var has_pos_back_backspace_control = user.has_pos_back_backspace_control;
                var has_pos_delete_order_control = user.has_pos_delete_order_control;

                // console.log("POS model: has_pos_price_control:",has_pos_price_control, ",has_pos_qty_control: ",
                //     has_pos_qty_control, ", has_pos_discount_control:", has_pos_discount_control,
                //     ", has_pos_back_backspace_control:", has_pos_back_backspace_control,
                //     ", has_pos_delete_order_control:",has_pos_delete_order_control);

                this.$el.find('.mode-button[data-mode="price"]')
                    .toggleClass('disabled-mode', !has_pos_price_control)
                    .prop('disabled', !has_pos_price_control);

                this.$el.find('.mode-button[data-mode="quantity"]')
                    .toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);

                this.$el.find('.mode-button[data-mode="quantity"]')
                    .toggleClass('selected-mode', has_pos_qty_control);

                this.$el.find('.zero').toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);

                //disable dot button
                // this.$el.find('.number-char').last().toggleClass('disabled-mode', !has_pos_qty_control)
                //     .prop('disabled', !has_pos_qty_control);
                console.log("===Numpadwidget apply access", user);


                this.$el.find('.numpad-minus').toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);



                this.$el.find('.mode-button[data-mode="discount"]').toggleClass('disabled-mode', !has_pos_discount_control)
                    .prop('disabled', !has_pos_discount_control);


                this.$el.find('.numpad-backspace')
                    .toggleClass('disabled-mode', !has_pos_back_backspace_control)
                    .prop('disabled', !has_pos_back_backspace_control);

                $('.deleteorder-button')
                    .css('display', (has_pos_delete_order_control)?'inline-block':'none');

            }

                
        },

        clickChangeMode: function (event) {
            this._super.apply(this, arguments);
            var user = this.pos.get_cashier();
            if(user != undefined){
                var has_pos_qty_control = user.has_pos_qty_control;
                var has_pos_price_control = user.has_pos_price_control;
                var has_pos_back_backspace_control = user.has_pos_back_backspace_control;

                // this.$el.find('.zero').toggleClass('disabled-mode', !has_pos_qty_control)
                //     .prop('disabled', !has_pos_qty_control);
                this.$el.find('.numpad-minus').toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);
                var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
                if (newMode === 'discount'){
                    var num_zero = this.$el.find('.zero');
                    num_zero.removeClass('disabled-mode');
                    num_zero.removeProp('disabled');
                }

            }
        },

    });

    //set_cashier(user)
    var _super_posmodel = pos_models.PosModel;
     pos_models.PosModel = pos_models.PosModel.extend({
        set_cashier: function(user){
            _super_posmodel.prototype.set_cashier.apply(this, arguments);
            this.applyAccessRights();

        },

         applyAccessRights: function () {
            //_super_posmodel.prototype.applyAccessRights.call(this);
            var user = this.get_cashier();
            console.log("--- POSMODEL:",user);
            if(user != undefined){
                var has_pos_price_control = user.has_pos_price_control;
                var has_pos_qty_control = user.has_pos_qty_control;
                var has_pos_discount_control = user.has_pos_discount_control;
                var has_pos_back_backspace_control = user.has_pos_back_backspace_control;
                var has_pos_delete_order_control = user.has_pos_delete_order_control;
                // console.log("POS model: has_pos_price_control:",has_pos_price_control, ",has_pos_qty_control: ",
                //     has_pos_qty_control, ", has_pos_discount_control:", has_pos_discount_control,
                //     ", has_pos_back_backspace_control:", has_pos_back_backspace_control,
                //     ", has_pos_delete_order_control:",has_pos_delete_order_control);

                $('.mode-button[data-mode="price"]')
                    .toggleClass('disabled-mode', !has_pos_price_control)
                    .prop('disabled', !has_pos_price_control);

                $('.mode-button[data-mode="quantity"]')
                    .toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);

                $('.mode-button[data-mode="quantity"]')
                    .toggleClass('selected-mode', has_pos_qty_control);

                $('.zero').toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);
                //disable dot button
                
                $('.number-char:last').toggleClass('disabled-mode', !has_pos_qty_control).prop('disabled', !has_pos_qty_control);
                console.log("===Pos model apply access",$('.number-char:last'),!has_pos_qty_control);

                $('.numpad-minus').toggleClass('disabled-mode', !has_pos_qty_control)
                    .prop('disabled', !has_pos_qty_control);

                $('.mode-button[data-mode="discount"]').toggleClass('disabled-mode', !has_pos_discount_control)
                    .prop('disabled', !has_pos_discount_control);


                $('.numpad-backspace')
                    .toggleClass('disabled-mode', !has_pos_back_backspace_control)
                    .prop('disabled', !has_pos_back_backspace_control);

                $('.deleteorder-button')
                    .css('display', (has_pos_delete_order_control)?'inline-block':'none');
            }


                
        },




        });


    //  chrome_pos.OrderSelectorWidget.include({
    //     deleteorder_click_handler: function(event, $el) {
    //         var user_c = this.pos.get_cashier();
    //             user_c.role_c = 'cashier';
    //             var users = this.pos.users;
    //             for(var i=0;i<users.length;i++){
    //              if(users[i].id == user_c.id){
    //                  user_c.role_c = users[i].role;
    //              }
    //             }
    //             var has_manager_pos = (user_c.role_c == 'manager');

    //         this.$('.deleteorder-button')
    //             .toggleClass('disabled-mode text-disb', !has_manager_pos)
    //             .prop('disabled', !has_manager_pos);
    //         if(has_manager_pos){
    //          this._super(event, $el);
    //         }else{
    //           return;
    //         }

    //     },
    // });
});