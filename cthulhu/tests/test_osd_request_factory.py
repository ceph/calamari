from django.utils.unittest import TestCase
from mock import MagicMock, patch

from cthulhu.manager.osd_request_factory import OsdRequestFactory
from cthulhu.manager.user_request import RadosRequest
from calamari_common.types import OSD_IMPLEMENTED_COMMANDS, OsdMap


class TestOSDFactory(TestCase):
    def setUp(self):
        fake_cluster_monitor = MagicMock()
        attributes = {'name': 'I am a fake',
                      'fsid': 12345,
                      'get_sync_object.return_value': fake_cluster_monitor,
                      'osds_by_id': {0: {'up': True}, 1: {'up': False}}}
        fake_cluster_monitor.configure_mock(**attributes)

        self.osd_request_factory = OsdRequestFactory(fake_cluster_monitor)

    def testCreate(self):
        self.assertNotEqual(OsdRequestFactory(0), None, 'Test creating an OSDRequest')

    def testScrub(self):
        scrub = self.osd_request_factory.scrub(0)
        self.assertIsInstance(scrub, RadosRequest, 'Testing Scrub')

        remote_mock = MagicMock()

        def get_remote():
            return remote_mock

        with patch('cthulhu.manager.user_request.get_remote', get_remote):
            scrub.submit(54321)

        remote_mock.run_job.assert_called_with(54321,
                                               'ceph.rados_commands',
                                               {'fsid': 12345,
                                                'cluster_name': 'I am a fake',
                                                'commands': [('osd scrub', {'who': '0'})]})

    def testDeepScrub(self):
        deep_scrub = self.osd_request_factory.deep_scrub(0)
        self.assertIsInstance(deep_scrub, RadosRequest, 'Failed to make a deep scrub request')

    def test_validate_scrub(self):
        self.assertEqual(self.osd_request_factory.get_valid_commands([0]), {0: {'valid_commands': OSD_IMPLEMENTED_COMMANDS}})

    def test_validate_scrub_on_down_osd(self):
        self.assertEqual(self.osd_request_factory.get_valid_commands([1]), {1: {'valid_commands': []}})

    def test_validate_op_key_error(self):
        self.assertRaises(KeyError, self.osd_request_factory.get_valid_commands, [2])


class TestOsdMapUpdates(TestCase):
    def setUp(self):
        fake_cluster_monitor = MagicMock()
        attributes = {'name': 'I am a fake',
                      'fsid': 12345,
                      'get_sync_object.return_value': fake_cluster_monitor,
                      'osds_by_id': {0: {'up': True}, 1: {'up': False}}}
        fake_cluster_monitor.configure_mock(**attributes)
        self.osd_map = OsdMap(1, None)
        self.factory = OsdRequestFactory(fake_cluster_monitor)

    def test_no_op(self):
        self.assertEqual([], self.factory._commands_to_set_flags(self.osd_map, {}))

    def test_unset_one(self):
        self.osd_map.flags['noup'] = True
        self.assertEqual([('osd unset', {'key': 'noup'})],
                         self.factory._commands_to_set_flags(self.osd_map, {'noup': False}))

    def test_set_one(self):
        self.osd_map.flags['noup'] = False
        self.assertEqual([('osd set', {'key': 'noup'})],
                         self.factory._commands_to_set_flags(self.osd_map, {'noup': True}))

    def test_set_one_that_is_already_set(self):
        self.osd_map.flags['noup'] = True
        self.assertEqual([],
                         self.factory._commands_to_set_flags(self.osd_map, {'noup': True}))

    def test_unset_one_that_is_not_set(self):
        self.assertEqual([],
                         self.factory._commands_to_set_flags(self.osd_map, {'noup': False}))

    def test_set_something_not_valid(self):
        self.assertRaises(RuntimeError,
                          self.factory._commands_to_set_flags, self.osd_map, {'nom': True})

    def test_set_and_unset_many(self):
        self.osd_map.flags['noscrub'] = True
        self.osd_map.flags['norecover'] = True

        self.assertEqual([('osd set', {'key': 'noup'}),
                          ('osd set', {'key': 'pause'}),
                          ('osd unset', {'key': 'noscrub'}),
                          ('osd unset', {'key': 'norecover'})],
                         self.factory._commands_to_set_flags(self.osd_map,
                                                             {'noscrub': False,
                                                              'norecover': False,
                                                              'noup': True,
                                                              'pause': True}))
