/*global define */
define(['underscore', 'jquery', 'backbone'], function(_, $, Backbone) {
    'use strict';

    var LoginBox = Backbone.View.extend({
        events: {},
        initialize: function() {},
        render: function() {}
    });
    return {
        loginBox: new LoginBox({
            el: '.loginBox'
        })
    };
});
