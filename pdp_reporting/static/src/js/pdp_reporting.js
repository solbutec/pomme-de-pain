odoo.define('aspl_pos_combo.pos', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var gui = require('point_of_sale.gui');
	var screens = require('point_of_sale.screens');
	var PopupWidget = require('point_of_sale.popups');
	var PosBaseWidget = require('point_of_sale.BaseWidget');

    var core = require('web.core');
    var rpc = require('web.rpc');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');
    var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;

    var QWeb = core.qweb;
    var _t = core._t;

    var round_pr = utils.round_precision;

    // ---------------------------------
    // --- printing interface
    //todo: ActionButtonWidget add button next to 'custumer', 'rewards', 'note'
    var ShowPosReportingUi = screens.ActionButtonWidget.extend({
        template : 'ShowPosReportingUi',
        button_click : function() {
            self = this;
            self.gui.show_screen('pos_reporting_ui');//, {users : users});
        },
    });

    screens.define_action_button({
        'name' : 'showposreportingui',
        'widget' : ShowPosReportingUi,
        'condition': function(){
            return true;//get_cashier().team_lead
        },
    });

    var ShowPosReportingUiWidget = screens.ScreenWidget.extend({
        template: 'ShowPosReportingUiWidget',
        previous_screen: 'products',
        events: {
            'click .button.back':  'click_back',
            'click #print_report_button': 'print_report',
            'change #type-reporting': 'change_type_report',
            //'click #edit_order': 'click_edit_order',
            //'click .searchbox .search-clear': 'clear_search',
            //'click #re_order_duplicate': 'click_duplicate_order',
            //'click #delete_draft_sale_note': 'click_delete_sale_note',
            //'keyup .searchbox input': 'search_order',
        },
        get_users: function(){
            //for  user in self.pos.users
        },
        init: function(parent, options){
            var self = this;

            this._super(parent, options);
            if(this.pos.config.iface_vkeyboard && self.chrome.widget.keyboard){
                self.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
        },
        click_back: function(event){
            this.gui.show_screen(this.previous_screen);//home
        },
        show: function(){
            var self = this;
            //console.log("=====HEllo====")
            //console.log(this.pos.get_order());
            //this.pos.get_order().show_orders = true;
             //this.pos.bind('change:selectedOrder';);
             //this.pos.get_order().trigger('change');
            this._super();
            //this.reload_orders();
        },

        print_report: function(event){
            alert("Print report");
        },
        change_type_report: function(event){
            var value = $('#type-reporting').val();
            alert("change type rapport 2", value);
            console.log("Self pos", self.pos);
            console.log($('#type-reporting'));
        },

    });
    gui.define_screen({name:'pos_reporting_ui', widget: ShowPosReportingUiWidget});


});