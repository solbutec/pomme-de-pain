odoo.define('pos_user_control.models', function (require) {
    "use strict";
    var module = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var models = module.PosModel.prototype.models;
    for (var i = 0; i < models.length; i++) {
        var model = models[i];
        if (model.model === 'res.users') {
            model.fields.push('has_pos_price_control');
            model.fields.push('has_pos_qty_control');
            model.fields.push('has_pos_back_backspace_control');
            model.fields.push('has_pos_delete_order_control');
        }
    }

    screens.NumpadWidget.include({

        init: function (parent, options) {
            this._super(parent, options);
        },

        applyAccessRights: function () {
            this._super();
            var user = this.pos.get_cashier();
            var has_pos_price_control = user.has_pos_price_control;
            var has_pos_qty_control = user.has_pos_qty_control;
            var has_pos_back_backspace_control = user.has_pos_back_backspace_control;
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
            this.$el.find('.numpad-backspace')
                .toggleClass('disabled-mode', !has_pos_back_backspace_control)
                .prop('disabled', !has_pos_back_backspace_control);
        },

        clickChangeMode: function (event) {
            this._super.apply(this, arguments);
            var user = this.pos.get_cashier();
            var has_pos_qty_control = user.has_pos_qty_control;
            this.$el.find('.zero').toggleClass('disabled-mode', !has_pos_qty_control)
                .prop('disabled', !has_pos_qty_control);
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            if (newMode === 'discount'){
                var num_zero = this.$el.find('.zero');
                num_zero.removeClass('disabled-mode');
                num_zero.removeProp('disabled')
            }
        }

    });
});