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

    // LET'S START CODING
    models.load_fields("res.users", ['pos_config_ids', ]);
    var _super_posmodel = models.PosModel.prototype;
  // override original class with extended one
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
          var self = this;
          _super_posmodel.initialize.apply(this, arguments);
          //console.log(self);
          //update users : ['pos_config_ids','in', [current.config.id]]
          
      },
    });

});
