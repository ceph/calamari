/* global _ */
'use strict';

var userController = function($rootScope, $scope, userSrv) {
        $rootScope.activeTab = 'user';
        $scope.title = $rootScope.pageTitle;
        $scope.dashboard = $rootScope.dashboard;
        var userDefaults = {
            username: 'admin',
            email: 'calamari@inktank.com',
            displayName: 'Calamari Admin',
            password: '',
            confirm: ''
        };
        $scope.user = {};
        angular.extend($scope.user, userDefaults);

        function clear() {
            angular.extend($scope.user, userDefaults);
        }

        function update(user) {
            userSrv.update(user).success(function() {
                refreshUserInfo();
            }).error(function(data) {
                _.each(data, function(value, key) {
                    $scope[key + 'ErrorMsg'] = _.first(value);
                    $scope[key + 'Error'] = true;
                });
            });
        }

        $scope.clear = clear;
        $scope.update = update;
        function refreshUserInfo() {
            userSrv.read().success(function(data) {
                angular.extend($scope.user, data);
                angular.extend(userDefaults, data);
            });
        }
        refreshUserInfo();
    };
userController.$inject = ['$rootScope', '$scope', 'userSrv'];
angular.module('adminApp').controller('UserCtrl', userController);

var userService = function($http) {
        var baseURL = '/api/v1/user/me';
        return {
            read: function() {
                return $http({
                    method: 'GET',
                    url: baseURL
                });
            },
            update: function(user) {
                return $http({
                    method: 'PUT',
                    url: baseURL,
                    data: JSON.stringify(user)
                });
            }
        };
    };
angular.module('adminApp').factory('userSrv', ['$http', userService]);
