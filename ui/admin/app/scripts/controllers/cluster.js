'use strict';

angular.module('adminApp').controller('ClusterCtrl', function($scope) {
    $scope.menus = [

    {
        label: 'General',
        clazz: '',
        url: '#/general'
    },

    {
        label: 'Cluster',
        clazz: 'active',
        url: '#/cluster'
    },

    {
        label: 'User',
        clazz: '',
        url: '#/user'
    }

    ];
});
