'use strict';

angular.module('adminApp').controller('UsersCtrl', function($scope, menus) {
    $scope.title = 'Users';
    $scope.menus = menus.menu('users');
});
