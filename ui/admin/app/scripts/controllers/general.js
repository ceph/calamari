'use strict';

angular.module('adminApp').controller('GeneralCtrl', function($scope, menus) {
    $scope.title = 'General';
    $scope.menus = menus.menu('general');
});
