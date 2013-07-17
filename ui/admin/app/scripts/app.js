'use strict';

angular.module('adminApp', [], function($provide) {
    $provide.factory('menus', function() {
        return {
            menu: function(active) {
                var labels = ['General', 'Cluster', 'User', 'Users'];
                var url = ['general', 'cluster', 'user', 'users'];
                var res = [];
                for (var i = 0; i < url.length; ++i) {
                    res.push({
                        label: labels[i],
                        clazz: url[i] === active ? 'active' : '',
                        url: '/#/' + url[i]
                    });
                }
                return res;
            }
        };
    });

}).config(function($routeProvider) {

    $routeProvider.when('/user', {
        templateUrl: 'views/user.html',
        controller: 'UserCtrl'
    }).when('/general', {
        templateUrl: 'views/general.html',
        controller: 'GeneralCtrl'
    }).when('/cluster', {
        templateUrl: 'views/cluster.html',
        controller: 'ClusterCtrl'
    }).when('/users', {
        templateUrl: 'views/users.html',
        controller: 'UsersCtrl'
    })
    .otherwise({
        redirectTo: '/user'
    });

});
