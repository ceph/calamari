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
            _.bindAll(this, 'loginHandler', 'loginToggle');
        },
        render: function() {
            this.ui.username = this.$('input[name="username"]');
            this.ui.password = this.$('input[name="password"]');
            this.ui.submit = this.$('input[type="submit"]');
            if (this.ui.username.val().length > 0 || this.ui.password.val().length > 0) {
                this.ui.submit.removeAttr('disabled');
            }
        },
        cookieName: 'XSRF-TOKEN',
        headerName: 'X-XSRF-TOKEN',
        loginUrl: '/api/v1/auth/login/',
        nextUrl: '/static/index.html',
        loginHandler: function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            var d = $.ajax(this.loginUrl);
            var self = this;
            d.then(function() {
                var csrf = $.cookie(self.cookieName);
                var headers = {};
                headers[self.headerName] = csrf;
                return $.ajax(self.loginUrl, {
                    data: {
                        username: self.ui.username.val(),
                        password: self.ui.password.val(),
                        // TODO we need a protected URL to test auth
                        next: self.nextUrl
                    },
                    type: 'POST',
                    headers: headers,
                    statusCode: {
                        400: function() {
                            // place holder
                            console.log('authentication failed');
                        },
                        200: function() {
                            // place holder
                            console.log('authentication successful');
                        }
                    }
                });
            }, function(error) {
                console.log('error during auth ', error);
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
