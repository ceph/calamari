'use strict';

var clusterController = function($rootScope, $scope, $http, $timeout) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'cluster';
        $scope.loaded = false;
        $timeout(function() {
            if ($scope.loaded === false) {
                $scope.loading = true;
            }
        }, 125);
        $http.get('api/v1/cluster').success(function(data) {
            $scope.clusters = data;
            $scope.loaded = true;
            $scope.loading = false;
        });
    };
angular.module('adminApp').controller('ClusterCtrl', ['$rootScope', '$scope', '$http', '$timeout', clusterController]);
