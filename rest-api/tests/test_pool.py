import mock
import logging

from django.utils.unittest import TestCase
from calamari_rest.views.v2 import PoolViewSet, POOL

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
