'use strict';

var generalController = function($scope, $http, menus) {
        $scope.title = 'General';
        $scope.menus = menus.menu('general');
        $http.get('api/v1/general').success(function(data) {
            $scope.general = data;
        });
    };
angular.module('adminApp').controller('GeneralCtrl', ['$scope', '$http', 'menus', generalController]);
