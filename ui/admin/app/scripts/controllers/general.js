'use strict';

var generalController = function($rootScope, $scope, $http, menus) {
        $scope.title = $rootScope.pageTitle;
        $scope.menus = menus.menu('general');
        $http.get('api/v1/general').success(function(data) {
            $scope.general = data;
        });
    };
angular.module('adminApp').controller('GeneralCtrl', ['$rootScope', '$scope', '$http', 'menus', generalController]);
