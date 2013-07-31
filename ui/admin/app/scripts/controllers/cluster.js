/* global _ */
'use strict';

var clusterController = function($rootScope, $scope, $http, $timeout, $filter, $dialog) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'cluster';

        $scope.loaded = false;
        $scope.editEnabled = false;
        $scope.removeEnabled = false;
        $scope.addEnabled = true;
        $timeout(function() {
            if ($scope.loaded === false) {
                $scope.loading = true;
            }
        }, 125);
        var refreshClusterList = function() {
                $http.get('/api/v1/cluster').success(function(data) {
                    if (data.length === 0) {
                        $scope.addClusterOpen = true;
                    }
                    $scope.clusters = data;
                    $scope.loaded = true;
                    $scope.loading = false;
                });
            };
        refreshClusterList();
        $scope.updateControls = function(cluster) {
            console.log(cluster);
            if (!cluster.checked) {
                $scope.editEnabled = false;
                $scope.removeEnabled = false;
                $scope.addEnabled = true;
                return;
            }
            $scope.editEnabled = true;
            $scope.removeEnabled = true;
            $scope.addEnabled = false;
            _.each($scope.clusters, function(c) {
                if (cluster.id === c.id) {
                    return c;
                }
                c.checked = false;
            });
            console.log($filter('filter')($scope.clusters, {
                checked: true
            }));
        };
        $scope.addOpen = function() {
            $scope.cluster = {};
            $scope.addClusterOpen = true;
        };
        $scope.addClose = function() {
            $scope.addClusterOpen = false;
        };
        $scope.addCluster = function(cluster) {
            console.log('Adding ' + cluster);
            $scope.addClusterOpen = false;
            $scope.loading = true;
            $scope.allDisabled = true;
            $http({
                method: 'POST',
                url: '/api/v1/cluster',
                data: JSON.stringify(cluster)
            }).success(function() {
                refreshClusterList();
                $scope.allDisabled = false;
                $scope.loading = false;
            }).error(function() {
                $scope.allDisabled = false;
                $scope.loading = false;
            });
        };
        $scope.editOpen = function() {
            var selected = $filter('filter')($scope.clusters, {
                checked: true
            });
            $scope.cluster = selected[0];
            $scope.editClusterOpen = true;
        };
        $scope.editClose = function() {
            $scope.editClusterOpen = false;
        };
        $scope.opts = {
            backdropFade: true,
            dialogFade: true
        };
        $scope.editCluster = function(cluster) {
            console.log('saving ' + cluster);
            $scope.editClusterOpen = false;
            $scope.loading = true;
            $scope.allDisabled = true;
            $http({
                method: 'PUT',
                url: '/api/v1/cluster/' + cluster.id,
                data: JSON.stringify(cluster)
            }).success(function() {
                refreshClusterList();
                $scope.allDisabled = false;
                $scope.loading = false;
            }).error(function() {
                $scope.allDisabled = false;
                $scope.loading = false;
            });
        };
        $scope.dialogOpts = {
            backdrop: true,
            keyboard: true,
            backdropClick: true,
            templateUrl: 'views/removeCluster.html',
            controller: 'RemoveDialogController',
            resolve: {
                cluster: function() {
                    var selected = $filter('filter')($scope.clusters, {
                        checked: true
                    });
                    return selected[0];
                }
            }
        };
        $scope.removeOpen = function() {
            var d = $dialog.dialog($scope.dialogOpts);
            d.open().then(function(cluster) {
                console.log(cluster);
                if (cluster.id === undefined) {
                    return;
                }
                $scope.loading = true;
                $scope.allDisabled = true;
                $http({
                    method: 'DELETE',
                    url: '/api/v1/cluster/' + cluster.id
                }).success(function() {
                    refreshClusterList();
                    $scope.allDisabled = false;
                    $scope.loading = false;
                    $scope.editEnabled = false;
                    $scope.removeEnabled = false;
                    $scope.addEnabled = true;
                }).error(function() {
                    $scope.allDisabled = false;
                    $scope.loading = false;
                    $scope.editEnabled = false;
                    $scope.removeEnabled = false;
                    $scope.addEnabled = true;
                });

            });
        };
    };
angular.module('adminApp').controller('ClusterCtrl', ['$rootScope', '$scope', '$http', '$timeout', '$filter', '$dialog', clusterController]);

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
