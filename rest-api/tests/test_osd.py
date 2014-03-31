
import urllib
from gevent.event import AsyncResult
import mock
import logging

from calamari_common.types import OSD
from tests.rest_api_unit_test import RestApiUnitTest

log = logging.getLogger(__name__)


def fake_async(obj):
    asr = AsyncResult()
    asr.set(obj)
    return asr


class TestOsd(RestApiUnitTest):
    SERVERS = ['server1', 'server2', 'server3']

    def setUp(self):
        super(TestOsd, self).setUp()

        self.rpc.list = mock.Mock(return_value=fake_async([]))
        self.rpc.get_sync_object = mock.Mock(return_value=fake_async([]))
        self.rpc.get_valid_commands = mock.Mock(return_value=fake_async([]))
        self.rpc.server_by_service = mock.Mock(return_value=fake_async([]))

    def test_filter_by_pool(self):
        fsid = "abc123"
        pool = 2

        response = self.client.get("/api/v2/cluster/{0}/osd?{1}".format(
            fsid,
            urllib.urlencode([("pool", pool)])
        ))

        self.assertStatus(response, 200)
        self.rpc.list.assert_called_once_with(fsid, OSD, {'pool': pool}, async=True)

        # NB no actual results in response because of mocking, just checking the filter
        # args are constructed through to point of RPC

    def test_filter_by_ids(self):
        fsid = "abc123"
        ids = [3, 1, 4]

        response = self.client.get("/api/v2/cluster/{0}/osd?{1}".format(
            fsid,
            urllib.urlencode([("id__in[]", i) for i in ids])
        ))

        self.assertStatus(response, 200)
        self.rpc.list.assert_called_once_with(fsid, OSD, {'id__in': ids}, async=True)

        # NB no actual results in response because of mocking, just checking the filter
        # args are constructed through to point of RPC
