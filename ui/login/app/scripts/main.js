require.config({
    paths: {
        jquery: '../bower_components/jquery/jquery',
        underscore: '../bower_components/underscore/underscore',
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
        }
    }
});

require(['app', 'underscore', 'jquery', 'backbone', 'bootstrap'], function(app, _, $, Backbone) {
    'use strict';
    console.log(Backbone);
    // use app here
    console.log(app);
    console.log('Running jQuery %s', $().jquery);
});
