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
});
