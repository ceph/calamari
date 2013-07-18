'use strict';

var usersController = function($scope, $http, menus) {
        $scope.title = 'Users';
        $scope.menus = menus.menu('users');
        $http.get('api/v1/user').success(function(data) {
            $scope.users = data;
        });
    };
angular.module('adminApp').controller('UsersCtrl', ['$scope', '$http', 'menus', usersController]);
