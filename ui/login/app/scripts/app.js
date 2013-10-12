/*global define */
define(['underscore', 'jquery', 'backbone', 'gitcommit', 'jquery.cookie'], function(_, $, Backbone, gitcommit) {
    'use strict';

    var LoginBox = Backbone.View.extend({
        events: {
            'click input[type="submit"]': 'loginHandler',
            'submit form': 'loginHandler',
            'keyup input[name="username"],input[name="password"]': 'loginToggle'
        },
        ui: {},
        initialize: function() {
            _.bindAll(this, 'loginHandler', 'loginToggle', 'toJSON', 'disableSubmit', 'enableSubmit', 'showErrors', 'hideErrors');
        },
        render: function() {
            this.ui.username = this.$('input[name="username"]');
            this.ui.password = this.$('input[name="password"]');
            this.ui.submit = this.$('button[type="submit"]');
            this.ui.errors = this.$('.errors');
            if (this.ui.username.val().length > 0 || this.ui.password.val().length > 0) {
                this.ui.submit.removeAttr('disabled');
            }
        },
        xsrfCookieName: 'XSRF-TOKEN',
        xsrfHeaderName: 'X-XSRF-TOKEN',
        loginUrl: '/api/v1/auth/login/',
        nextUrl: '/dashboard/',
        toJSON: function() {
            return JSON.stringify({
                username: this.ui.username.val(),
                password: this.ui.password.val(),
                next: this.nextUrl
            });
        },
        loginHandler: function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            // get session and xsrf cookie values
            var get = $.get(this.loginUrl),
                self = this;
            this.disableSubmit('icon-spinner icon-spin');
            this.hideErrors();
            get.then(function() {
                var xsrfToken = $.cookie(self.xsrfCookieName);
                var headers = {};
                headers[self.xsrfHeaderName] = xsrfToken;
                return $.ajax(self.loginUrl, {
                    type: 'POST',
                    contentType: 'application/json; charset=utf-8',
                    headers: headers,
                    data: self.toJSON(),
                    statusCode: {
                        200: function(resp) {
                            // Normal Path
                            window.location = resp.next ?  resp.next : self.nextUrl;
                        },
                        401: function(jqxhr) {
                            // Normal Error
                            var resp = JSON.parse(jqxhr.responseText);
                            self.showErrors(resp.message);
                        }
                    }
                });
            }, function(jqxhr, statusTxt, error) {
                // All other errors
                self.showErrors(jqxhr.statusCode().status + ' ' + error);
            }).always(function() {
                self.enableSubmit('icon-ok');
            });
            return false;
        },
        hideErrors: function() {
            this.ui.errors.fadeOut().css('visibility', 'hidden');
        },
        showErrors: function(msg) {
            var errors = this.ui.errors;
            errors.text(msg).css('visibility', 'visible').hide().fadeIn();
        },
        disableSubmit: function(iconClazz) {
            this.ui.submit.attr('disabled', 'disabled').addClass('disabled').html('<i class="' + iconClazz + ' icon-large"></i>');
        },
        enableSubmit: function(iconClazz) {
            this.ui.submit.removeAttr('disabled').removeClass('disabled').html('<i class="' + iconClazz + ' icon-large"></i>');
        },
        loginToggle: function() {
            var username = this.ui.username,
                password = this.ui.password;
            if (username.val().length > 0 && password.val().length > 0) {
                this.enableSubmit('icon-ok');
                return;
            }
            this.disableSubmit('icon-ban-circle');
        }
    });

    var loginBox = new LoginBox({
        el: '.loginBox'
    });
    loginBox.render();
    window.inktank = {
        commit: gitcommit['git-commit']
    };
    return {
        LoginBox: loginBox
    };
});
