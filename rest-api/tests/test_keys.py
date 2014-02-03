
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
import mock

import ceph.views.rpc_view


class RestApiUnitTest(TestCase):
    def setUp(self):
        # Patch in a mock for RPCs
        rpc = mock.Mock()
        self.rpc = rpc
        old_init = ceph.views.rpc_view.RPCViewSet.__init__

        def init(_self, *args, **kwargs):
            old_init(_self, *args, **kwargs)
            _self.client = rpc

        self._old_init = old_init
        ceph.views.rpc_view.RPCViewSet.__init__ = init

        # Create a user to log in as
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin')

        # A client for performing requests to the API
        self.client = APIClient()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        ceph.views.rpc_view.RPCViewSet.__init__ = self._old_init


class TestKey(RestApiUnitTest):
    def test_list_patch(self):
        response = self.client.patch("/api/v2/key", [
            {'id': 'minion1', 'status': 'accepted'},
            {'id': 'minion2', 'status': 'accepted'}
        ], format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Should have called through to approve
        self.assertListEqual(self.rpc.minion_accept.call_args_list, [
            mock.call('minion1'),
            mock.call('minion2')
        ])

    def test_list_delete(self):
        response = self.client.delete("/api/v2/key", [
            {'id': 'minion1'},
            {'id': 'minion2'}
        ], format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Should have called through to approve
        self.assertListEqual(self.rpc.minion_delete.call_args_list, [
            mock.call('minion1'),
            mock.call('minion2')
        ])
