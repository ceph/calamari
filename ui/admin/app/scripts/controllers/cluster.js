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
        $http.get('/api/v1/cluster').success(function(data) {
            if (data.length === 0) {
                $scope.addClusterOpen = true;
            }
            $scope.clusters = data;
            $scope.loaded = true;
            $scope.loading = false;
        });
        $scope.openAdd = function() {
            $scope.addClusterOpen = true;
        };
        $scope.closeAdd = function() {
            $scope.addClusterOpen = false;
        };
        $scope.openEdit = function() {
            $scope.cluster = {
                name: 'cluster 1',
                uri: 'http://cluster'
            };
            $scope.editClusterOpen = true;
        };
        $scope.closeEdit = function() {
            $scope.editClusterOpen = false;
        };
        $scope.opts = {
            backdropFade: true,
            dialogFade: true
        };
    };
angular.module('adminApp').controller('ClusterCtrl', ['$rootScope', '$scope', '$http', '$timeout', clusterController]);
