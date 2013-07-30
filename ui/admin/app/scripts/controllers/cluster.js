'use strict';

var clusterController = function($rootScope, $scope, $http, $timeout, $dialog) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'cluster';
        $scope.loaded = false;
        $timeout(function() {
            if ($scope.loaded === false) {
                $scope.loading = true;
            }
        }, 125);
        var refresh = function() {
                $http.get('/api/v1/cluster').success(function(data) {
                    if (data.length === 0) {
                        $scope.addClusterOpen = true;
                    }
                    $scope.clusters = data;
                    $scope.loaded = true;
                    $scope.loading = false;
                });
            };
        refresh();
        $scope.openAdd = function() {
            $scope.addClusterOpen = true;
        };
        $scope.closeAdd = function() {
            $scope.addClusterOpen = false;
        };
        $scope.clusterAdd = function(cluster) {
            console.log('Adding ' + cluster);
            $scope.addClusterOpen = false;
            $scope.loading = true;
            $scope.allDisabled = true;
            $http({
                method: 'POST',
                url: '/api/v1/cluster',
                data: JSON.stringify({
                    'name': cluster.name,
                    'api_base_url': cluster.uri
                })
            }).success(function() {
                refresh();
                $scope.allDisabled = false;
                $scope.loading = false;
            }).error(function() {
                $scope.allDisabled = false;
                $scope.loading = false;
            });
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
        $scope.dialogOpts = {
            backdrop: true,
            keyboard: true,
            backdropClick: true,
            templateUrl: 'views/removeCluster.html',
            controller: 'RemoveDialogController',
            resolve: {
                cluster: function() {
                    return {
                        name: 'my cluster',
                        id: 10
                    };
                }
            }
        };
        $scope.openRemove = function() {
            var d = $dialog.dialog($scope.dialogOpts);
            d.open().then(function(result) {
                //$scope.loading = true;
                console.log(result);

            });
        };
    };
angular.module('adminApp').controller('ClusterCtrl', ['$rootScope', '$scope', '$http', '$timeout', '$dialog', clusterController]);

var removeDialogController = function($scope, dialog, cluster) {
        $scope.cluster = cluster;
        $scope.closeRemove = function() {
            dialog.close({});
        };
        $scope.clusterRemove = function(cluster) {
            dialog.close(cluster);
        };
    };
angular.module('adminApp').controller('RemoveDialogController', ['$scope', 'dialog', 'cluster', removeDialogController]);
