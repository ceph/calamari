'use strict';

var clusterController = function($rootScope, $scope, $http, menus) {
        $scope.title = $rootScope.pageTitle;
        $scope.menus = menus.menu('cluster');
        $http.get('api/v1/cluster').success(function(data) {
            $scope.clusters = data;
        });
    };
angular.module('adminApp').controller('ClusterCtrl', ['$rootScope', '$scope', '$http', 'menus', clusterController]);
