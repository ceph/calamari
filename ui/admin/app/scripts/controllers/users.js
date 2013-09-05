/* global _ */
'use strict';

var usersController = function($rootScope, $scope, $http) {
        $scope.title = $rootScope.pageTitle;
        $rootScope.activeTab = 'users';
        $scope.dashboard = $rootScope.dashboard;
        $http.get('/api/v1/user').success(function(data) {
            $scope.users = data;
        });
        $scope.allUsers = false;
        $scope.toggleUsers = function() {
            _.each($scope.users, function(user) {
                user.checked = $scope.allUsers;
            });
        };
        $scope.updateControls = function() {
            var selected = _.reduce($scope.users, function(memo, user) {
                return user.checked ? memo + 1 : memo;
            }, 0);
            $scope.allUsers = selected === $scope.users.length;
        };
        $scope.opts = {
            backdropFade: true,
            dialogFade: true
        };
        $scope.addUserOpen = false;
        $scope.openAdd = function() {
            $scope.addUserOpen = true;
        };
        $scope.closeAdd = function() {
            $scope.addUserOpen = false;
        };
        $scope.userAdd = function(user) {
            $scope.addUserOpen = false;
            console.log(user);
        };
    };
angular.module('adminApp').controller('UsersCtrl', ['$rootScope', '$scope', '$http', usersController]);
