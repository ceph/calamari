/*global define */
define(['underscore', 'jquery', 'backbone'], function(_, $, Backbone) {
    'use strict';

    var LoginBox = Backbone.View.extend({
        events: {
            'click input[type="submit"]': 'loginHandler',
            'keyup input[name="username"],input[name="password"]': 'loginToggle'
        },
        ui: {},
        initialize: function() {
            this.ui.username = this.$('input[name="username"]');
            this.ui.password = this.$('input[name="password"]');
            this.ui.submit = this.$('input[type="submit"]');
            _.bindAll(this, 'loginHandler', 'loginToggle');
        },
        render: function() {},
        loginHandler: function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            return false;
        },
        loginToggle: function() {
            if (this.ui.username.val().length > 0 && this.ui.password.val().length > 0) {
                this.ui.submit.removeAttr('disabled');
                return;
            }
            this.ui.submit.attr('disabled','disabled');
        }
    });
    var loginBox = new LoginBox({
        el: '.loginBox'
    });
    loginBox.render();
    return {
        LoginBox: loginBox
    };
});
