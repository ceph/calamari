
from rest_framework import status
import mock

from tests.rest_api_unit_test import RestApiUnitTest


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
