from django.utils.unittest import TestCase
from mock import MagicMock, patch
from cthulhu.manager.rpc import RpcInterface


class TestRpc(TestCase):

    def setUp(self):
        fake_manager = MagicMock

        mock_attribs =  {'name': 'I am a fake',
                      'fsid': 12345,
                      'clusters': fake_manager,
                      12345: fake_manager,
                      'osd_tree_node_by_id': {1: 'a node'},
                      'get_sync_object.return_value': fake_manager,
                      'osds_by_id': {0: {'up': True}, 1: {'up': False}}}

        fake_manager.configure_mock(**mock_attribs)
        self.rpc = RpcInterface(fake_manager)

    def test_get_sync_object_happy_path(self):

        osd_map = self.rpc.get_sync_object(12345, 'osd_map', ['osd_tree_node_by_id'])
        assert osd_map == {1: 'a node'}