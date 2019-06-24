

odoo.define('pos_customer_display.customer_display', function(require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var core = require('web.core');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var _t = core._t;
    var PosModelSuper = models.PosModel;
    //console.log("CUSTOMER DISPLAY JS: BEGIN");
    models.PosModel = models.PosModel.extend({
        prepare_text_customer_display: function(type, data){
        console.log("== prepare_text_customer_display (type, data):",type, data);
            if (this.config.iface_customer_display != true)
                return;
            var line_length = this.config.customer_display_line_length || 20;
            var currency_rounding = this.currency.decimals;

            if (type == 'add_update_line'){
                var line = data['line'];
                var price_unit = line.get_unit_price();
                var discount = line.get_discount();
                if (discount) {
                    price_unit = price_unit * (1.0 - (discount / 100.0));
                    }
                price_unit = price_unit.toFixed(currency_rounding);
                var qty = line.get_quantity();
                // only display decimals when qty is not an integer
                if (qty.toFixed(0) == qty) {
                    qty = qty.toFixed(0);
                }
                // only display unit when != Unit(s)
                var unit = line.get_unit();
                var unit_display = '';
                if (unit && !unit.is_unit) {
                    unit_display = unit.name;
                }
                //var l21 = qty + unit_display + ' x ' + price_unit;
                var l21 = qty  + ' x ' + price_unit;
                var l22 = ' ' + line.get_display_price().toFixed(currency_rounding);
                var lines_to_send = new Array(
                    this.proxy.align_left(line.get_product().display_name, line_length),
                    this.proxy.align_left(l21, line_length - l22.length) + l22
                    );

            } else if (type == 'remove_orderline') {
                // first click on the backspace button set the amount to 0 => we can't precise the deleted qunatity and price
                var line = data['line'];
                var lines_to_send = new Array(
                    this.proxy.align_left(_t("Delete Item"), line_length),
                    this.proxy.align_right(line.get_product().display_name, line_length)
                    );

            } else if (type == 'add_paymentline') {
                var total = this.get('selectedOrder').get_total_with_tax().toFixed(currency_rounding);
                var lines_to_send = new Array(
                    this.proxy.align_left(_t("TOTAL: "), line_length),
                    this.proxy.align_right(total, line_length)
                    );

            } else if (type == 'remove_paymentline') {
                var line = data['line'];
                var amount = line.get_amount().toFixed(currency_rounding);
                var lines_to_send = new Array(
                    this.proxy.align_left(_t("Cancel Payment"), line_length),
                    this.proxy.align_right(line.cashregister.journal_id[1] , line_length - 1 - amount.length) + ' ' + amount
                    );

            } else if (type == 'update_payment') {
                var change = data['change'];
                var lines_to_send = new Array(
                    this.proxy.align_left(_t("Your Change:"), line_length),
                    this.proxy.align_right(change, line_length)
                );

            } else if (type == 'push_order') {
                var lines_to_send = new Array(
                    this.proxy.align_center(this.config.customer_display_msg_next_l1, line_length),
                    this.proxy.align_center(this.config.customer_display_msg_next_l2, line_length)
                    );

            } else if (type == 'openPOS') {
                var lines_to_send = new Array(
                    this.proxy.align_center(this.config.customer_display_msg_next_l1, line_length),
                    this.proxy.align_center(this.config.customer_display_msg_next_l2, line_length)
                    );

            } else if (type = 'closePOS') {
                var lines_to_send = new Array(
                    this.proxy.align_center(this.config.customer_display_msg_closed_l1, line_length),
                    this.proxy.align_center(this.config.customer_display_msg_closed_l2, line_length)
                    );
            } else {
                console.warn('KZM: Unknown message type (POS customer display)');
                return;
            }

            var lam1 = lines_to_send[0].split(" ").join("-");
            var lam2 = lines_to_send[1].split(" ").join("-");
            console.log("===== BEFORE SEND TO DISPLAY CLIENT, LENGTH:",(lam1+lam2).length,"::",(lam1+lam2));
            $.post("http://localhost:8000/com/send", {
                port: 'COM6',
                band: 9600,
                msg: lam1+lam2,
            })
            //alert("AFTER");
            //this.proxy.send_text_customer_display(lines_to_send, line_length);
        },

        push_order: function(order){
            var res = PosModelSuper.prototype.push_order.call(this, order);
            if (order) {
                this.prepare_text_customer_display('push_order', {'order' : order});
            }
            return res;
        },

    });

    devices.ProxyDevice = devices.ProxyDevice.extend({
        send_text_customer_display: function(data, line_length){
        console.log("== send_text_customer_display: (data, line_length):",data, line_length);
            //FIXME : this function is call twice. The first time, it is not called by prepare_text_customer_display : WHY ?
            if (_.isEmpty(data) || data.length != 2 || data[0].length != line_length || data[1].length != line_length){
                console.warn("KZM: send_text_customer_display: Bad Data argument. Data=" + data + ' line_length=' + line_length);
            } else {
//              alert(JSON.stringify(data));
                return this.message('send_text_customer_display', {'text_to_display' : JSON.stringify(data)});
            }
        },

        align_left: function(string, length){
            if (string) {
                if (string.length > length)
                {
                    string = string.substring(0,length);
                }
                else if (string.length < length)
                {
                    while(string.length < length)
                        string = string + ' ';
                }
            }
            else {
                string = ' '
                while(string.length < length)
                    string = ' ' + string;
            }
            return string;
        },

        align_right: function(string, length){
        //console.log("== align_right: (string, length): ",string, length);
            if (string) {
                if (string.length > length)
                {
                    string = string.substring(0,length);
                }
                else if (string.length < length)
                {
                    while(string.length < length)
                        string = ' ' + string;
                }
            }
            else {
                string = ' '
                while(string.length < length)
                    string = ' ' + string;
            }
            return string;
        },

        align_center: function(string, length){
        //console.log("== align_center: (string, length): ",string, length);
            if (string) {
                if (string.length > length)
                {
                    string = string.substring(0, length);
                }
                else if (string.length < length)
                {
                    var ini = (length - string.length) / 2;
                    while(string.length < length - ini)
                        string = ' ' + string;
                    while(string.length < length)
                        string = string + ' ';
                }
            }
            else {
                string = ' '
                while(string.length < length)
                    string = ' ' + string;
            }
            return string;
        },
    });

    var OrderlineSuper = models.Orderline;

    models.Orderline = models.Orderline.extend({
        /* set_quantity() is called when you force the qty via the dedicated button
        AND when you create a new order line via add_product().
        So, when you add a product, we call prepare_text_customer_display() twice...
        but I haven't found any good solution to avoid this -- Alexis */
        set_quantity: function(quantity){
        //console.log("== set_quantity: (quantity): ",quantity);
            var res = OrderlineSuper.prototype.set_quantity.call(this, quantity);
            if (quantity != 'remove') {
                var line = this;
                if(this.selected){
                    this.pos.prepare_text_customer_display('add_update_line', {'line': line});
                }
            }
            return res;
        },

        set_discount: function(discount){
        //console.log("== set_discount: (discount): ",discount);
            var res = OrderlineSuper.prototype.set_discount.call(this, discount);
            if (discount) {
                var line = this;
                if(this.selected){
                    this.pos.prepare_text_customer_display('add_update_line', {'line': line});
                }
            }
            return res;
        },

        set_unit_price: function(price){
        console.log("== set_unit_price: (price): ",price);
            var res = OrderlineSuper.prototype.set_unit_price.call(this, price);
            var line = this;
            if(this.selected){
                this.pos.prepare_text_customer_display('add_update_line', {'line': line});
            }
            return res;
        },

    });

    var OrderSuper = models.Order;

    models.Order = models.Order.extend({
        add_product: function(product, options){
        console.log("== set_unit_price: (product, options): ",product, options);
            var res = OrderSuper.prototype.add_product.call(this, product, options);
            if (product) {
                var line = this.get_last_orderline();
                this.pos.prepare_text_customer_display('add_update_line', {'line' : line});
            }
            return res;
        },

        remove_orderline: function(line){
        console.log("== remove_orderline: (line): ",line);
            if (line) {
                this.pos.prepare_text_customer_display('remove_orderline', {'line' : line});
            }
            return OrderSuper.prototype.remove_orderline.call(this, line);
        },

        remove_paymentline: function(line){
        console.log("== remove_paymentline: (line): ",line);
            if (line) {
                this.pos.prepare_text_customer_display('remove_paymentline', {'line' : line});
            }
            return OrderSuper.prototype.remove_paymentline.call(this, line);
        },

        add_paymentline: function(cashregister){
        console.log("== add_paymentline: (cashregister): ",cashregister);
            var res = OrderSuper.prototype.add_paymentline.call(this, cashregister);
            if (cashregister) {
                this.pos.prepare_text_customer_display('add_paymentline', {'cashregister' : cashregister});
            }
            return res;
        },

    });

    screens.PaymentScreenWidget.include({
        render_paymentlines: function(){
        console.log("== render_paymentlines: (): ");
            var res = this._super();
            var currentOrder = this.pos.get_order();
            if (currentOrder) {
                var paidTotal = currentOrder.get_total_paid();
                var dueTotal = currentOrder.get_total_with_tax();
                var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
                if (change) {
                    var change_rounded = change.toFixed(2);
                    this.pos.prepare_text_customer_display('update_payment', {'change': change_rounded});
                }
            }
            return res;
        },
    });

    gui.Gui.include({
        close: function(){
            this._super();
            console.log("== close: : ");
            this.pos.prepare_text_customer_display('closePOS', {});
        },
    });

    chrome.ProxyStatusWidget.include({
        start: function(){
            this._super();
            console.log("== start: : ");
            this.pos.prepare_text_customer_display('openPOS', {});
        },
    });

    screens.PaymentScreenWidget.include({
        show: function(){
            this._super();
            console.log("== show: : ");
            this.pos.prepare_text_customer_display('add_paymentline', {});
        },
    });
 //console.log("CUSTOMER DISPLAY JS: END");
});
