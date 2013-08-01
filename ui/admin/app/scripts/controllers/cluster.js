/* global _ */
/* jshint -W106 */
'use strict';

function editClusterController($rootScope, $scope, $http) {
    $scope.editClusterOpen = false;
    $scope.showModal = function(evt, cluster) {
        console.log(cluster);
        $scope.cluster = cluster;
        $scope.editClusterOpen = true;
    };
    $scope.hideModal = function() {
        $scope.editClusterOpen = false;
    };
    $scope.$on('edit:open', $scope.showModal);
    $scope.$on('edit:close', $scope.hideModal);
    $scope.opts = {
        backdropFade: true,
        dialogFade: true
    };
    $scope.editCluster = function(cluster) {
        console.log('saving ' + cluster);
        $scope.editClusterOpen = false;
        $scope.$parent.$broadcast('cluster:loading');
        $http({
            method: 'PUT',
            url: '/api/v1/cluster/' + cluster.id,
            data: JSON.stringify(cluster)
        }).success(function() {
            $scope.$parent.$broadcast('cluster:refresh');
        }).error(function() {
            $scope.allDisabled = false;
            $scope.loading = false;
        });
    };
}
angular.module('adminApp').controller('editClusterController', ['$rootScope', '$scope', '$http', editClusterController]);

function addClusterController($rootScope, $scope, $http) {
    $scope.addClusterOpen = false;
    $scope.opts = {
        backdropFade: true,
        dialogFade: true
    };

    $scope.$on('add:open', function() {
        $scope.addClusterOpen = true;
    });

    $scope.addClose = function() {
        $scope.addClusterOpen = false;
    };
    $scope.addCluster = function(cluster) {
        console.log('Adding ' + cluster);
        $scope.loading = true;
        $scope.allDisabled = true;
        $scope.nameError = false;
        $scope.api_base_urlError = false;
        $http({
            method: 'POST',
            url: '/api/v1/cluster',
            data: JSON.stringify(cluster)
        }).success(function() {
            $scope.$parent.$broadcast('cluster:refresh');
            $scope.loading = false;
            $scope.addClusterOpen = false;
        }).error(function(data) {
            _.each(data, function(value, key) {
                $scope[key + 'ErrorMsg'] = _.first(value);
                $scope[key + 'Error'] = true;
            });
            $scope.allDisabled = false;
            $scope.loading = false;
        });
    };
}
angular.module('adminApp').controller('addClusterController', ['$rootScope', '$scope', '$http', addClusterController]);

var clusterController = function($rootScope, $scope, $http, $timeout, $filter, $dialog) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'cluster';
        $scope.loaded = false;
        $scope.editEnabled = false;
        $scope.removeEnabled = false;
        $scope.addEnabled = true;

        function refreshClusterList() {
            $http.get('/api/v1/cluster').success(function(data) {
                if (data.length === 0) {
                    $scope.$broadcast('add:open');
                    return;
                }
                $scope.clusters = data;
                $scope.loaded = true;
                $scope.loading = false;
            });
        }

        $scope.updateControls = function(cluster) {
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
        };

        $scope.$on('cluster:refresh', refreshClusterList);
        $scope.$on('cluster:loading', function() {
            $scope.allDisabled = true;
            $scope.loaded = false;
        });

        $timeout(function() {
            if ($scope.loaded === false) {
                $scope.loading = true;
            }
        }, 125);

        $scope.editOpen = function() {
            var selected = $filter('filter')($scope.clusters, {
                checked: true
            });
            $scope.$broadcast('edit:open', selected[0]);
        };

        $scope.addOpen = function() {
            $scope.$broadcast('add:open');
        };

        function resetControls() {
            $scope.allDisabled = false;
            $scope.loading = false;
            $scope.editEnabled = false;
            $scope.removeEnabled = false;
            $scope.addEnabled = true;
        }
        $scope.$on('controls:reset', resetControls);

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
                    $scope.$broadcast('cluster:refresh');
                    $scope.$broadcast('controls:reset');
                }).error(function() {
                    $scope.$broadcast('cluster:refresh');
                    $scope.$broadcast('controls:reset');
                });

            });
        };

        refreshClusterList();
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
