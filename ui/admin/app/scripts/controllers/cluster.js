'use strict';

angular.module('adminApp').controller('ClusterCtrl', function($scope, menus) {
    $scope.title = 'Cluster';
    $scope.menus = menus.menu('cluster');
});
