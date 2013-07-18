'use strict';

var clusterController = function($scope, menus) {
        $scope.title = 'Cluster';
        $scope.menus = menus.menu('cluster');
    };
clusterController.$inject = ['$scope', 'menus'];
angular.module('adminApp').controller('ClusterCtrl', clusterController);
