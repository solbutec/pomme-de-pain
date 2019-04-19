odoo.define('amh_payement_currencies.pos', function (require) {
	"use strict";

	var gui = require('point_of_sale.gui');
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var chrome = require('point_of_sale.chrome');
	var core = require('web.core');
	var DB = require('point_of_sale.DB');
	var keyboard = require('point_of_sale.keyboard').OnscreenKeyboardWidget;
	var rpc = require('web.rpc');
	var utils = require('web.utils');
    var field_utils = require('web.field_utils');
	var PopupWidget = require('point_of_sale.popups');
	var bus_service = require('bus.BusService');
    var bus = require('bus.Longpolling');
    var session = require('web.session');

	var QWeb = core.qweb;
	var _t = core._t;
	var round_pr = utils.round_precision;

	var _super_paymentline = models.Paymentline;
	models.Paymentline = models.Paymentline.extend({
            initialize: function(attributes, options) {
                _super_paymentline.prototype.initialize.call(this, attributes, options);
                this.change_currency = 0;
                this.due_currency = 0;
                this.amount_due = 0;
                this.amount_change = 0;

                //add the others fields
            },
//            init_from_JSON: function(json){
//                this.change_currency = json.change_currency;
//                this.due_currency = this.pos.due_currency;
//                this.amount_due = this.amount_due;
//            },
                export_as_JSON: function(){
                   var new_val = {};
                   var res = _super_paymentline.prototype.export_as_JSON.call(this);
                   res['change_currency'] = this.change_currency;
                   res['due_currency'] = this.due_currency;
                   res['amount_due'] = this.amount_due;
                   res['amount_change'] = this.amount_change;
                   return res;
            },

//            //exports as JSON for receipt printing
//            export_for_printing: function(){
//                return {
//                    amount: this.get_amount(),
//                    journal: this.cashregister.journal_id[1],
//                };
//            },
        });

    // ====== MODELS ================

    var _super_posModel = models.PosModel;
	 models.PosModel = models.PosModel.extend({
	    initialize: function(session, attributes) {
            _super_posModel.prototype.initialize.call(this, session, attributes);
            this.all_currencies = [];
            this.enable_conversion = false;
        },
        set_enable_conversion: function(enable_conversion){
          this.enable_conversion = enable_conversion;
        },
        get_enable_conversion: function(){
          return this.enable_conversion;
        },
        });

	 models.PosModel.prototype.models.push({
                model: 'res.currency',
                fields: ['name','symbol','position','rounding','rate'],
                //ids:    function(self){ return [self.config.currency_id[0], self.company.currency_id[0]]; },
                loaded: function(self, currencies){
                    self.all_currencies = currencies;
                    self.currency = _.findWhere(currencies, {id: self.config.currency_id[0]});
                    if (self.currency.rounding > 0 && self.currency.rounding < 1) {
                        self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                    } else {
                        self.currency.decimals = 0;
                    }

                    //self.company_currency = _.findWhere(currencies, {id: self.company.currency_id[0]});
                },
            });

     // ====== SCREENS ================

      screens.PaymentScreenWidget.include({
         get_currency_rate_by_id: function(curr_id){
         console.log("vuuuuurenciiiies",this.pos.all_currencies);
            var cur =  this.pos.all_currencies.filter(function(obj){
                            return obj.id == curr_id;
                           });
             if(cur.length > 0)
                return cur[0].rate;
             return 1;
         },

         payment_input: function(input) {
          var self = this;
            console.log("PAYMENT INPUT :"+input);
            //this._super(input);
            //alert("NUMPAD! CLICK");
            var newbuf = this.gui.numpad_input(this.inputbuffer, input, {'firstinput': this.firstinput});

            this.firstinput = (newbuf.length === 0);

            // popup block inputs to prevent sneak editing.
            if (this.gui.has_popup()) {
                return;
            }

            if (newbuf !== this.inputbuffer) {
                this.inputbuffer = newbuf;
                var order = this.pos.get_order();
                if (order.selected_paymentline) {
                    var amount = this.inputbuffer;

                    if (this.inputbuffer !== "-") {
                        amount = field_utils.parse.float(this.inputbuffer);
                        //-- AMH-ADDED

                        if(this.pos.get_enable_conversion()){
                            $('#amount_in_currency').val(amount);

                             var curr_id = parseInt($('#curency_choosed').val());
                             var curr_rate =self.get_currency_rate_by_id(curr_id);
                             order.selected_paymentline.change_currency = curr_id;
                           // console.log("cuuuuuurr ratedd",curr_rate);
                            var main_curr_rate = parseFloat(this.pos.currency.rate);
                            //console.log("maiiiiiiiiin",main_curr_rate);
                            amount = amount * curr_rate / main_curr_rate;
                             //console.log("amoooount",amount);
                            order.selected_paymentline.amount_change=amount*main_curr_rate/curr_rate;

                            }
                        //--END AMH-ADDED

                    }

                    order.selected_paymentline.set_amount(amount);
                    this.order_changes();
                    this.render_paymentlines();

                    //-- AMH-ADDED
                        if(this.pos.get_enable_conversion()){
                            var curr_id = parseInt($('#curency_choosed').val());
                            var return_curency_choosed_id = parseInt($('#return_curency_choosed').val());
                            order.selected_paymentline.due_currency = return_curency_choosed_id;
                            var curr_rate = self.get_currency_rate_by_id(curr_id);
                             var return_curency_choosed_rate = self.get_currency_rate_by_id(return_curency_choosed_id);

                           // console.log("=========CURR "+curr_id);

                             //return_curency_choosed_rate = _.findWhere(self.pos.all_currencies, {id: curr_id}).rate;
                            /* for(var cr = 0; cr < self.pos.all_currencies.length ; i++){
                             if(cr.id == return_curency_choosed_rate_id){
                               return_curency_choosed_rate = cr.rate;
                             }*/
                             console.log("return currency_choosed_rate",return_curency_choosed_rate);
                            var main_curr_rate = parseFloat(this.pos.currency.rate);
                            console.log("main_curr_rate",main_curr_rate);
                            var due_curr = (order.get_due()) * main_curr_rate / curr_rate;
                            console.log("due_curr",due_curr);
                            var revenu_curr_check_due = (order.get_due()) * main_curr_rate / return_curency_choosed_rate;
                            console.log("revenu_curr_check_due",revenu_curr_check_due);
                            var extra_due_curr = (order.get_due()) * main_curr_rate / curr_rate;
                            $('#revenu_curr').val(due_curr.toFixed(3));
                            $('#revenu_curr_check').val(revenu_curr_check_due.toFixed(3));
                            if(due_curr <= 0){
                                 $('#revenu_curr').css("background-color", "#6EC89B");
                            }else{
                                $('#revenu_curr').css("background-color", "white");
                            }
                            if(revenu_curr_check_due <= 0){
                                 $('#revenu_curr_check').css("background-color", "#6EC89B");
                                 order.selected_paymentline.amount_due = revenu_curr_check_due;
                            }else{
                                $('#revenu_curr_check').css("background-color", "white");
                            }
                        }
                    //--END AMH-ADDED

                    this.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(amount));
                }
            }
        },
      });

      //gui.define_screen({name:'payment', widget: screens.PaymentScreenWidget});

//      chrome.Chrome.include({
//		events: {
//            "change #enable_convert": "change_enable_convert",
//            "change #curency_choosed": "change_chosen_currency",
//            "change #return_curency_choosed": "change_chosen_currency",
//		},
//		change_enable_convert: function(event){
//			var self = this;
//			self.pos.set_enable_conversion(event.currentTarget.checked);
//			 if(event.currentTarget.checked){
//			      $('.trans-currencies').removeClass('amh-display-none');
//			 }else{
//			    $('.trans-currencies').addClass('amh-display-none');
//			 }
//
//		},
//		change_chosen_currency: function(event){
//			var self = this;
//			// --- Refresh the values ----------
//			self.screens.payment.payment_input('1');
//			self.screens.payment.payment_input('BACKSPACE');
//			// --- Ens refresh the values ------
//
//            //TODO : DONE: WHEN THE CURRENCY CHANGED WE MUST TO UPDATES VALUES IN PAYMENT LINE (call payment_input from PaymentScreenWidget)
//
//		},
//
//		});
//
});
