'use strict';

angular.module('adminApp', [])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/user', {
        templateUrl: 'views/user.html',
        controller: 'UserCtrl'
      })
      .when('/general', {
        templateUrl: 'views/general.html',
        controller: 'GeneralCtrl'
      })
      .when('/cluster', {
        templateUrl: 'views/cluster.html',
        controller: 'ClusterCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
