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

    def test_retrieve_crushmap(self):
        self.request.method = 'GET'
        response = self.cmvs.retrieve(self.request, 12345)
        self.assertEqual(response.status_code, 200)

    def test_replace_crushmap_passes_validation(self):
        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            cmvs = CrushMapViewSet()

        cmvs.serializer_class = mock.Mock()
        cmvs.serializer_class.return_value = cmvs.serializer_class
        cmvs.serializer_class.is_valid.return_value = True

        self.request.method = 'POST'
        self.request.DATA = {}
        response = cmvs.replace(self.request, 12345)
        self.assertEqual(response.status_code, 200)

    def test_replace_crushmap_fails_validation(self):
        with mock.patch('calamari_rest.views.v2.RPCViewSet'):
            cmvs = CrushMapViewSet()

        cmvs.serializer_class = mock.Mock()
        cmvs.serializer_class.return_value = cmvs.serializer_class
        cmvs.serializer_class.is_valid.return_value = False

        self.request.method = 'POST'
        self.request.DATA = {}
        response = cmvs.replace(self.request, 12345)
        self.assertEqual(response.status_code, 400)
