'use strict';

var adminApp = angular.module('adminApp', ['ui.bootstrap']);
adminApp.config(function($routeProvider) {

    $routeProvider.when('/user', {
        templateUrl: 'views/user.html',
        title: 'User Settings',
        controller: 'UserCtrl'
    }).when('/general', {
        templateUrl: 'views/general.html',
        title: 'General Settings',
        controller: 'GeneralCtrl'
    }).when('/cluster', {
        templateUrl: 'views/cluster.html',
        title: 'Cluster Settings',
        controller: 'ClusterCtrl'
    }).when('/users', {
        templateUrl: 'views/users.html',
        title: 'Users Settings',
        controller: 'UsersCtrl'
    }).otherwise({
        redirectTo: '/user'
    });

});
adminApp.factory('menus', function() {
    return {
        menu: function() {
            var labels = ['General', 'Cluster', 'User'];
            var url = ['general', 'cluster', 'user'];
            var res = [];
            for (var i = 0; i < url.length; ++i) {
                res.push({
                    label: labels[i],
                    url: '#/' + url[i]
                });
            }
            return res;
        }
    };
});
adminApp.run(function($rootScope, $route, menus) {
    $rootScope.menus = menus.menu();
    $rootScope.dashboard = function() {
        window.document.location = '/dashboard/';
    };
    $rootScope.$on('$routeChangeSuccess', function() {
        $rootScope.pageTitle = $route.current.title;
    });
});
