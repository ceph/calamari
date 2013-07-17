'use strict';

angular.module('adminApp').controller('UserCtrl', function($scope) {
    $scope.menus = [{
        label: 'General',
        clazz: '',
        url: '#/general'
    }, {
        label: 'Cluster',
        clazz: '',
        url: '#/cluster'
    }, {
        label: 'User',
        clazz: 'active',
        url: '#/user'
    }];
    $scope.clear = function() {
        $scope.user.email = 'calamari@inktank.com';
        $scope.user.password = '';
        $scope.user.displayName = 'Calamari Admin';
        $scope.user.confirm = '';
    };
    $scope.user = {
        name: 'admin',
        email: 'calamari@inktank.com',
        displayName: 'Calamari Admin',
        password: '',
        confirm: ''
    };
});
