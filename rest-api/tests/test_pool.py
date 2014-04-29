import mock
import logging

from django.utils.unittest import TestCase
from calamari_rest.views.v2 import PoolViewSet, POOL

log = logging.getLogger(__name__)


def fake_list(*args, **kwargs):
    return [{'pool_name': 'data'}]


class TestPoolValidation(TestCase):

    def setUp(self):
        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            self.pvs = PoolViewSet()
            self.pvs.client = mock.MagicMock()
            self.pvs.client.list = fake_list
            self.pvs.client.create.return_value = ['request_id']

    def test_create_duplicate_names_fails_validation(self):
        request = mock.Mock()
        request.method = 'PUT'
        request.DATA = {'name': 'data', 'pg_num': 64}

        response = self.pvs.create(request, 12345)
        self.assertEqual(response.status_code, 409)

    def test_create_with_pg_num_as_string(self):
        request = mock.Mock()
        request.method = 'PUT'
        request.DATA = {'name': 'not_data', 'pg_num': '64'}

        response = self.pvs.create(request, 12345)
        self.assertEqual(response.status_code, 202)

        self.pvs.client.create.assert_called_with(12345, POOL, {'name': 'not_data', 'pg_num': 64})

    def test_create_passes_validation(self):
        request = mock.Mock()
        request.method = 'PUT'
        request.DATA = {'name': 'not_data', 'pg_num': 64}

        response = self.pvs.create(request, 12345)
        self.assertEqual(response.status_code, 202)

    def test_filter_serializer_defaults(self):
        request = mock.Mock()
        request.method = 'PUT'
        request.DATA = {'name': 'not_data', 'pg_num': 64}

        self.pvs.create(request, 12345)

        self.pvs.client.create.assert_called_with(12345, POOL, {'name': 'not_data', 'pg_num': 64})