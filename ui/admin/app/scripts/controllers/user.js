'use strict';

var userController = function($rootScope, $scope) {
        $rootScope.activeTab = 'user';
        $scope.title = $rootScope.pageTitle;
        $scope.dashboard = $rootScope.dashboard;
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
userController.$inject = ['$rootScope', '$scope', 'menus'];
angular.module('adminApp').controller('UserCtrl', userController);
