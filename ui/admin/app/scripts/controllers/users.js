'use strict';

var usersController = function($rootScope, $scope, $http, menus) {
        $scope.title = $rootScope.pageTitle;
        $scope.menus = menus.menu('users');
        $http.get('api/v1/user').success(function(data) {
            $scope.users = data;
        });
    };
angular.module('adminApp').controller('UsersCtrl', ['$rootScope', '$scope', '$http', 'menus', usersController]);
