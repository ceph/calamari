/* global _ */
'use strict';

var clusterController = function($rootScope, $scope, $http, $timeout, $filter, $dialog) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'cluster';
        $scope.loaded = false;
        $scope.editDisabled = true;
        $scope.removeDisabled = true;
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
        $scope.showSelected = function(cluster) {
            console.log(cluster);
            if (!cluster.checked) {
                $scope.editDisabled = true;
                $scope.removeDisabled = true;
                $scope.addDisabled = false;
                return;
            }
            $scope.editDisabled = false;
            $scope.removeDisabled = false;
            $scope.addDisabled = true;
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
        $scope.openAdd = function() {
            $scope.cluster = {};
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
                data: JSON.stringify(cluster)
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
            var selected = $filter('filter')($scope.clusters, {
                checked: true
            });
            $scope.cluster = selected[0];
            $scope.editClusterOpen = true;
        };
        $scope.closeEdit = function() {
            $scope.editClusterOpen = false;
        };
        $scope.opts = {
            backdropFade: true,
            dialogFade: true
        };
        $scope.clusterEdit = function(cluster) {
            console.log('saving ' + cluster);
            $scope.editClusterOpen = false;
            $scope.loading = true;
            $scope.allDisabled = true;
            $http({
                method: 'PUT',
                url: '/api/v1/cluster/' + cluster.id,
                data: JSON.stringify(cluster)
            }).success(function() {
                refresh();
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
        $scope.openRemove = function() {
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
                    refresh();
                    $scope.allDisabled = false;
                    $scope.loading = false;
                }).error(function() {
                    $scope.allDisabled = false;
                    $scope.loading = false;
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
