odoo.define('test.test', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var _t = core._t;

var careOfButton = screens.ActionButtonWidget.extend({
    template: 'careOfButton',
    button_click: function(){
        var self = this;
        this.gui.show_popup('selection',{
            'title': 'Welcome to JS world',

        });
    },

});

screens.define_action_button({
        'name': 'careOfButton',
        'widget': careOfButton,
    });

});


