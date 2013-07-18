'use strict';

var usersController = function($scope, menus) {
        $scope.title = 'Users';
        $scope.menus = menus.menu('users');
    };
usersController.$inject = ['$scope', 'menus'];
angular.module('adminApp').controller('UsersCtrl', usersController);
