require.config({
    paths: {
        jquery: '../bower_components/jquery/jquery',
        'jquery.cookie': '../bower_components/jquery.cookie/jquery.cookie',
        underscore: '../bower_components/underscore-amd/underscore',
        backbone: '../bower_components/backbone/backbone',
        bootstrap: 'vendor/bootstrap'
    },
    shim: {
        bootstrap: {
            deps: ['jquery'],
            exports: 'jquery'
        },
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        'jquery.cookie': {
            deps: ['jquery']
        }
    }
});

require(['app'], function(app) {
    'use strict';
    // use app here
    window.app = app;
});
