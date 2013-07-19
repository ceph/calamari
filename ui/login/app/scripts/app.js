/*global define */
define(['underscore', 'jquery', 'backbone', 'jquery.cookie'], function(_, $, Backbone) {
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
            var d = $.ajax('/api/v1/auth/login/');
            d.then(function() {
                var csrf = $.cookie('csrftoken');
                return $.ajax('/api/v1/auth/login/', {
                    type: 'POST',
                    header: {
                        'X-CSRFToken': csrf
                    },
                    statusCode: {
                        403: function() {
                            console.log('authentication failed');
                        },
                        302: function() {
                            console.log('authentication successful');
                        }
                    }
                });
            }, function(error) {
                console.log('error ', error);
            });
            return false;
        },
        loginToggle: function() {
            var submit = this.ui.submit,
                username = this.ui.username,
                password = this.ui.password;
            if (username.val().length > 0 && password.val().length > 0) {
                submit.removeAttr('disabled');
                return;
            }
            submit.attr('disabled', 'disabled');
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
