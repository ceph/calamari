'use strict';

angular.module('adminApp').controller('GeneralCtrl', function($scope) {
    $scope.menus = [{
        label: 'General',
        clazz: 'active',
        url: '#/general'
    }, {
        label: 'Cluster',
        clazz: '',
        url: '#/cluster'
    }, {
        label: 'User',
        clazz: '',
        url: '#/user'
    }];
});
