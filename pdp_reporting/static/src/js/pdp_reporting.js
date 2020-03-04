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
        default_date_start: '',
        default_date_end: '',
        events: {
            'click .button.back':  'click_back',
            'click #print_report_button': 'print_report',
            'focus .amh-use-keyboard': 'connect_keyborad',
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
                //connect keyboard
                self.chrome.widget.keyboard.connect($('.amh-use-keyboard'));
            }
        },

        click_back: function(event){
            this.gui.show_screen(this.previous_screen);//home
        },
        connect_keyborad: function(event){
            if (self.pos.config.iface_vkeyboard && self.chrome.widget.keyboard) {
                self.chrome.widget.keyboard.connect($(event.currentTarget));
            }
        },
        show: function(options){
            var self = this;
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1).toString().padStart(2, '0')+'-'+today.getDate().toString().padStart(2, '0');
            var time = today.getHours().toString().padStart(2, '0') + ":" + today.getMinutes().toString().padStart(2, '0') + ":" + today.getSeconds().toString().padStart(2, '0');
            self.default_date_end = date+' '+time;
            self.default_date_start = date +' '+ '08:00:00';
            this._super(options);
            //connect keyborad
           /* console.log("SELCTORS:",$('#date_start_report'), "end",$('#date_end_report'));
            if (self.pos.config.iface_vkeyboard && self.chrome.widget.keyboard) {
                    self.chrome.widget.keyboard.connect($('#date_start_report'));
                    self.chrome.widget.keyboard.connect($('#date_end_report'));
            }*/
            this.renderElement();
            this.change_type_report();

        } ,

        renderElement: function(){
            var self = this;
            // get dates
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1).toString().padStart(2, '0')+'-'+today.getDate().toString().padStart(2, '0');
            var time = today.getHours().toString().padStart(2, '0') + ":" + today.getMinutes().toString().padStart(2, '0') + ":" + today.getSeconds().toString().padStart(2, '0');
            self.default_date_end = date+' '+time;
            self.default_date_start = date +' '+ '08:00:00';
            //
            this._super();
        },
        print_report: function(event){
            var date_start_report = ($("#date_start_report").val() || '').trim();
            var date_end_report = ($("#date_end_report").val() || '').trim();
            var type_reporting = ($("#type-reporting").val() || '').trim();
            var user_reporting = ($("#user-reporting").val() || '').trim();
            //console.log("Report:",date_start_report,"->", date_end_report, ":: ", type_reporting, "::", user_reporting);

            //get-from-backend
            //--- printing receipt
            this.pos.type_reporting = type_reporting;
            this.pos.user_reporting = user_reporting;
            this.pos.date_start_report = date_start_report;
            this.pos.date_end_report = date_end_report;
            this.gui.show_screen('receipt_reporting');

        },
        change_type_report: function(event){
            var type_reporting = ($("#type-reporting").val() || '').trim();
            console.log("--- type_reporting:::", type_reporting);
            if(type_reporting == 'main_ouvre_cais'){
                $('#user-reporting-cont').show();
            }else{
                $('#user-reporting-cont').hide();
            }
        },
    });
    gui.define_screen({name:'pos_reporting_ui', widget: ShowPosReportingUiWidget});



    //------------------ REPORT RECEIPT
    var ReceiptReportingScreenWidget = screens.ScreenWidget.extend({
        template: 'ReceiptReportingScreenWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent, options);
        },
        show: function(){
            this._super();
            var self = this;
            this.render_receipt();
            this.handle_auto_print();
        },
        handle_auto_print: function() {
            if (this.should_auto_print()) {
                this.print();
                if (this.should_close_immediately()){
                    this.click_next();
                }
            } else {
                this.lock_screen(false);
            }
        },
        should_auto_print: function() {
            return this.pos.config.iface_print_auto;
        },
        should_close_immediately: function() {
            return this.pos.config.iface_print_via_proxy && this.pos.config.iface_print_skip_screen;
        },
        lock_screen: function(locked) {
            this._locked = locked;
            if (locked) {
                this.$('.next').removeClass('highlight');
            } else {
                this.$('.next').addClass('highlight');
            }
        },
        get_receipt_render_env: function() {
            var self = this;

            var name= "", report_caissier = false, user_report=false;
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1).toString().padStart(2, '0')+'-'+today.getDate().toString().padStart(2, '0');
            var time = today.getHours().toString().padStart(2, '0') + ":" + today.getMinutes().toString().padStart(2, '0') + ":" + today.getSeconds().toString().padStart(2, '0');
            today = date+' '+time;
            var type_reporting = this.pos.type_reporting;
            var user_reporting = this.pos.user_reporting;
            var date_start_report = this.pos.date_start_report;
            var date_end_report = this.pos.date_end_report;
            if(type_reporting == 'main_ouvre_glob'){
                name = "Main courante global";
            }else if(type_reporting == 'main_ouvre_cais'){
                name = "Main courante";
                if(user_reporting){
                    user_report  = this.pos.users.find(utilisateur => utilisateur.id == user_reporting);
                }
            }
            // Get from backend
            var lines_to_print = [];
            rpc.query({
                    model: 'pos.config',
                    method: 'main_courant_rapport',
                    context: {
                        'pos_company_id': self.pos.company.id,
                        'pos_config_id': self.pos.config.id,
                        'type_reporting': type_reporting,
                        'user_reporting': user_reporting,
                        'date_start_report': date_start_report,
                        'date_end_report': date_end_report,
                    },
                }, {
                    async: false
                }).then(function(lines){
                     lines_to_print =  lines;
                });

            return {
                widget: this,
                pos: this.pos,
                receipt: this.export_for_printing(),
                report_name: name,
                date_now: today,
                report_caissier: report_caissier,
                report_type: type_reporting,//main_ouvre_cais
                report_user: user_report.name,
                pos_name : this.pos.config.name,
                lines: lines_to_print,
            };
        },
        print_web: function() {
            if ($.browser.safari) {
                document.execCommand('print', false, null);
            } else {
                try {
                    window.print();
                } catch(err) {
                    if (navigator.userAgent.toLowerCase().indexOf("android") > -1) {
                        this.gui.show_popup('error',{
                            'title':_t('Printing is not supported on some android browsers'),
                            'body': _t('Printing is not supported on some android browsers due to no default printing protocol is available. It is possible to print your tickets by making use of an IoT Box.'),
                        });
                    } else {
                        throw err;
                    }
                }
            }
            this.pos.get_order()._printed = true;
        },
        print_xml: function() {
            var receipt = QWeb.render('XmlReceipt', this.get_receipt_render_env());

            this.pos.proxy.print_receipt(receipt);
        },
        print: function() {
            var self = this;

            if (!this.pos.config.iface_print_via_proxy) { // browser (html) printing

                this.lock_screen(true);

                setTimeout(function(){
                    self.lock_screen(false);
                }, 1000);

                this.print_web();
            } else {    // proxy (xml) printing
                this.print_xml();
                this.lock_screen(false);
            }
        },
        click_next: function() {
            //this.pos.get_order().finalize();
            this.gui.show_screen("pos_reporting_ui");
        },
        click_back: function() {
            this.gui.show_screen("products");
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function(){
                if (!self._locked) {
                    self.click_next();
                }
            });
            this.$('.back').click(function(){
                if (!self._locked) {
                    self.click_back();
                }
            });
            this.$('.button.print').click(function(){
                if (!self._locked) {
                    self.print();
                }
            });
        },
  
        render_receipt: function() {
            this.$('.pos-receipt-container-reporting').html(QWeb.render('PosTicketReporting', this.get_receipt_render_env()));
        },

        export_for_printing: function(){
            var orderlines = [];
            var self = this;

            var paymentlines = [];
            var cashier = this.pos.get_cashier();
            var company = this.pos.company;
            var shop    = this.pos.shop;
            var date    = new Date();

            function is_xml(subreceipt){
                return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
            }

            function render_xml(subreceipt){
                if (!is_xml(subreceipt)) {
                    return subreceipt;
                } else {
                    subreceipt = subreceipt.split('\n').slice(1).join('\n');
                    var qweb = new QWeb2.Engine();
                        qweb.debug = config.debug;
                        qweb.default_dict = _.clone(QWeb.default_dict);
                        qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');

                    return qweb.render('subreceipt',{'pos':self.pos,'widget':self.pos.chrome,'order':self, 'receipt': receipt}) ;
                }
            }

            var receipt = {
                orderlines: orderlines,
                paymentlines: paymentlines,
                cashier: cashier ? cashier.name : null,
                precision: {
                    price: 2,
                    money: 2,
                    quantity: 3,
                },
                date: {
                    year: date.getFullYear(),
                    month: date.getMonth(),
                    date: date.getDate(),       // day of the month
                    day: date.getDay(),         // day of the week
                    hour: date.getHours(),
                    minute: date.getMinutes() ,
                    isostring: date.toISOString(),
                    localestring: date.toLocaleString(),
                },
                company:{
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    contact_address: company.partner_id[1],
                    vat: company.vat,
                    vat_label: company.country && company.country.vat_label || '',
                    name: company.name,
                    phone: company.phone,
                    logo:  this.pos.company_logo_base64,
                },
                shop:{
                    name: shop.name,
                },
                currency: this.pos.currency,
            };

            if (is_xml(this.pos.config.receipt_header)){
                receipt.header = '';
                receipt.header_xml = render_xml(this.pos.config.receipt_header);
            } else {
                receipt.header = this.pos.config.receipt_header || '';
            }

            if (is_xml(this.pos.config.receipt_footer)){
                receipt.footer = '';
                receipt.footer_xml = render_xml(this.pos.config.receipt_footer);
            } else {
                receipt.footer = this.pos.config.receipt_footer || '';
            }

            return receipt;
        },

    });
    gui.define_screen({name:'receipt_reporting', widget: ReceiptReportingScreenWidget});



});