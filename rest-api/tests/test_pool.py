import mock
import logging

from django.utils.unittest import TestCase
from calamari_rest.views.v2 import PoolViewSet, POOL
from tests.rest_api_unit_test import RestApiUnitTest, fake_async

log = logging.getLogger(__name__)


def fake_list(*args, **kwargs):
    return [{'pool_name': 'data',
             'pg_placement_num': 64,
             'pg_num': 64,
             'type': 1,
             'pool': 0,
             'size': 2}
            ]


class TestPoolValidation(TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.method = 'POST'

        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            self.pvs = PoolViewSet()
            self.pvs.client = mock.MagicMock()
            self.pvs.client.list = fake_list
            self.pvs.client.create.return_value = ['request_id']
            self.pvs.client.get.return_value = fake_list()[0]
            self.pvs.client.get_sync_object.return_value = {'mon_max_pool_pg_num': 65535}

    def test_create_duplicate_names_fails_validation(self):
        self.request.DATA = {'name': 'data', 'pg_num': 64}
        response = self.pvs.create(self.request, 12345)
        self.assertEqual(response.status_code, 409)

    def test_create_with_pg_num_as_string(self):
        self.request.DATA = {'name': 'not_data', 'pg_num': '64'}
        response = self.pvs.create(self.request, 12345)
        self.assertEqual(response.status_code, 202)
        self.pvs.client.create.assert_called_with(12345, POOL, {'name': 'not_data', 'pg_num': 64})

    def test_create_passes_validation(self):
        self.request.DATA = {'name': 'not_data', 'pg_num': 64}
        response = self.pvs.create(self.request, 12345)
        self.assertEqual(response.status_code, 202)
        self.pvs.client.create.assert_called_with(12345, POOL, {'name': 'not_data', 'pg_num': 64})

    def test_create_pgp_num_less_than_pg_num(self):
        self.request.DATA = {'name': 'not_data', 'pg_num': 64, 'pgp_num': 100}
        response = self.pvs.create(self.request, 12345)
        self.assertEqual(response.status_code, 400)

    def test_create_with_no_data(self):
        self.request.DATA = {}
        response = self.pvs.create(self.request, 12345)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'pg_num': 'Required during POST', 'name': 'Required during POST'})

    def test_create_pool_with_pg_num_greater_than_limit_setting_fails(self):
        self.request.DATA = {'name': 'not_data', 'pg_num': 65540}
        response = self.pvs.update(self.request, 12345, 0)
        self.assertEqual(response.status_code, 400)

    def test_update_pool_to_reduce_pg_num_fails(self):
        self.request.method = 'PATCH'
        self.request.DATA = {'pg_num': 16}
        response = self.pvs.update(self.request, 12345, 0)
        self.assertEqual(response.status_code, 400)

    def test_update_pool_to_reduce_pgp_num_fails(self):
        self.request.method = 'PATCH'
        self.request.DATA = {'pgp_num': 16}
        response = self.pvs.update(self.request, 12345, 0)
        self.assertEqual(response.status_code, 400)

    def test_update_name_duplication_fails(self):
        self.request.method = 'PATCH'
        self.request.DATA = {'name': 'data', 'pg_num': 64}
        response = self.pvs.update(self.request, 12345, 0)
        self.assertEqual(response.status_code, 409)

    def test_update_without_name_works(self):
        self.request.method = 'PATCH'
        self.request.DATA = {'pg_num': 65}
        response = self.pvs.update(self.request, 12345, 0)
        self.assertEqual(response.status_code, 202)


class TestPoolDefaults(RestApiUnitTest):
    FIREFLY_CONFIG = {
        'osd_pool_default_size': "3",
        'osd_pool_default_min_size': "2",
        'osd_pool_default_flag_hashpspool': "true",
        'osd_pool_default_crush_rule': "-1",
        'osd_pool_default_crush_replicated_ruleset': "0"
    }

    DUMPLING_CONFIG = {
        'osd_pool_default_size': "2",
        'osd_pool_default_min_size': "1",
        'osd_pool_default_flag_hashpspool': "false",
        'osd_pool_default_crush_rule': "0"
    }

    DUMPLING_DEFAULTS = {
        'name': None, 'id': None, 'size': 2, 'pg_num': None, 'crush_ruleset': 0,
        'min_size': 1, 'crash_replay_interval': 0, 'pgp_num': None, 'hashpspool': False,
        'full': None, 'quota_max_objects': 0, 'quota_max_bytes': 0
    }

    FIREFLY_DEFAULTS = {
        'name': None, 'id': None, 'size': 3, 'pg_num': None, 'crush_ruleset': 0,
        'min_size': 2, 'crash_replay_interval': 0, 'pgp_num': None, 'hashpspool': True,
        'full': None, 'quota_max_objects': 0, 'quota_max_bytes': 0
    }

    def setUp(self):
        super(TestPoolDefaults, self).setUp()

    def test_no_rules(self):
        self.rpc.get_sync_object = mock.Mock(return_value=fake_async({}))
        self.rpc.list = mock.Mock(return_value=fake_async([]))

        response = self.client.get("/api/v2/cluster/abc/pool?defaults")
        self.assertStatus(response, 503)

    def assert_defaults(self, expected):
        response = self.client.get("/api/v2/cluster/abc/pool?defaults")
        self.assertStatus(response, 200)
        self.assertDictEqual(response.data, expected)

    def test_dumpling(self):
        config = self.DUMPLING_CONFIG.copy()
        rules = [{'ruleset': 0}, {'ruleset': 1}, {'ruleset': 2}]

        self.rpc.get_sync_object = mock.Mock(return_value=fake_async(config))
        self.rpc.list = mock.Mock(return_value=fake_async(rules))

        self.assert_defaults(self.DUMPLING_DEFAULTS)

    def test_firefly(self):
        config = self.FIREFLY_CONFIG.copy()
        rules = [{'ruleset': 0}]

        self.rpc.get_sync_object = mock.Mock(return_value=fake_async(config))
        self.rpc.list = mock.Mock(return_value=fake_async(rules))

        self.assert_defaults(self.FIREFLY_DEFAULTS)

    def test_dumpling_bad_default(self):
        config = self.DUMPLING_CONFIG.copy()
        config['osd_pool_default_crush_rule'] = 0
        rules = [{'ruleset': 24}, {'ruleset': 23}]

        self.rpc.get_sync_object = mock.Mock(return_value=fake_async(config))
        self.rpc.list = mock.Mock(return_value=fake_async(rules))

        # Should pick the lowest numbered valid crush rule
        expected = self.DUMPLING_DEFAULTS.copy()
        expected['crush_ruleset'] = 23
        self.assert_defaults(expected)

    def test_firefly_bad_default(self):
        config = self.FIREFLY_CONFIG.copy()
        # Let the config try to use '0' which may not exist
        config['osd_pool_default_crush_replicated_ruleset'] = 0
        rules = [{'ruleset': 24}, {'ruleset': 23}]

        self.rpc.get_sync_object = mock.Mock(return_value=fake_async(config))
        self.rpc.list = mock.Mock(return_value=fake_async(rules))

        # Should pick the lowest numbered valid crush rule
        expected = self.FIREFLY_DEFAULTS.copy()
        expected['crush_ruleset'] = 23
        self.assert_defaults(expected)
