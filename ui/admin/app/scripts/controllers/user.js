'use strict';

var userController = function($scope, menus) {
        $scope.title = 'User';
        $scope.menus = menus.menu('user');
        $scope.clear = function() {
            $scope.user.email = 'calamari@inktank.com';
            $scope.user.password = '';
            $scope.user.displayName = 'Calamari Admin';
            $scope.user.confirm = '';
        };
        $scope.user = {
            name: 'admin',
            email: 'calamari@inktank.com',
            displayName: 'Calamari Admin',
            password: '',
            confirm: ''
        };
    };
userController.$inject = ['$scope', 'menus'];
angular.module('adminApp').controller('UserCtrl', userController);
