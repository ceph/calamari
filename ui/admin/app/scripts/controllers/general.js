'use strict';

var generalController = function($scope, menus) {
        $scope.title = 'General';
        $scope.menus = menus.menu('general');
    };
generalController.$inject = ['$scope', 'menus'];
angular.module('adminApp').controller('GeneralCtrl', generalController);
