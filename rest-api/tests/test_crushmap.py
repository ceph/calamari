import mock
import logging

from django.utils.unittest import TestCase
from calamari_rest.views.v2 import CrushMapViewSet

log = logging.getLogger(__name__)


class TestCrushMap(TestCase):

    def setUp(self):
        self.request = mock.Mock()

        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            self.cmvs = CrushMapViewSet()
            self.cmvs.client = mock.MagicMock()
            self.cmvs.client.update.return_value = {}

    def test_retrieve_crushmap(self):
        self.request.method = 'GET'
        response = self.cmvs.retrieve(self.request, 12345)
        self.assertEqual(response.status_code, 200)

    def test_replace_crushmap_passes(self):
        self.request.method = 'POST'
        self.request.DATA = {}
        response = self.cmvs.replace(self.request, 12345)
        self.assertEqual(response.status_code, 200)
