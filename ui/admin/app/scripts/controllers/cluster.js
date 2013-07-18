'use strict';

var clusterController = function($scope, $http, menus) {
        $scope.title = 'Cluster';
        $scope.menus = menus.menu('cluster');
        $http.get('api/v1/cluster').success(function(data) {
            $scope.clusters = data;
        });
    };
angular.module('adminApp').controller('ClusterCtrl', ['$scope', '$http', 'menus', clusterController]);
