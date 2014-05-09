import mock
import logging

from django.utils.unittest import TestCase
from calamari_rest.views.v2 import SaltKeyViewSet, ParseError

log = logging.getLogger(__name__)


def fake_list(*args, **kwargs):
    return [{'id': 'ubuntu',
             'status': 'pre'}
            ]


class TestSaltKeyValidation(TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.method = 'POST'

        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            self.viewset = SaltKeyViewSet()
            self.viewset.client = mock.MagicMock()
            self.viewset.client.list = fake_list
            self.viewset.client.get.return_value = fake_list()[0]

    def test_passing_one_to_list_bulk_update_fails_validation(self):
        self.request.DATA = {'id': 'ubuntu', 'status': 'accepted'}
        self.assertRaises(ParseError, self.viewset.list_partial_update, self.request)
