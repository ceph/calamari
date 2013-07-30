'use strict';

var generalController = function($rootScope, $scope, $http) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'general';
        $scope.loading = true;
        $http.get('/api/v1/info').success(function(data) {
            $scope.general = data;
            $scope.loading = false;
        });
    };
angular.module('adminApp').controller('GeneralCtrl', ['$rootScope', '$scope', '$http', generalController]);
