'use strict';

var usersController = function($rootScope, $scope, $http) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'users';
        $http.get('api/v1/user').success(function(data) {
            $scope.users = data;
        });
    };
angular.module('adminApp').controller('UsersCtrl', ['$rootScope', '$scope', '$http', usersController]);
