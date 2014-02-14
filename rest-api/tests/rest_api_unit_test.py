
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import TestCase
import mock

import calamari_rest.views.rpc_view


class RestApiUnitTest(TestCase):
    login = True  # Should setUp log in for us?
    USERNAME = 'admin'
    PASSWORD = 'admin'

    def setUp(self):
        # Patch in a mock for RPCs
        rpc = mock.Mock()
        self.rpc = rpc
        old_init = calamari_rest.views.rpc_view.RPCViewSet.__init__

        def init(_self, *args, **kwargs):
            old_init(_self, *args, **kwargs)
            _self.client = rpc

        self._old_init = old_init
        calamari_rest.views.rpc_view.RPCViewSet.__init__ = init

        # Create a user to log in as
        User.objects.create_superuser(self.USERNAME, 'admin@admin.com', self.PASSWORD)

        # A client for performing requests to the API
        self.client = APIClient()
        if self.login:
            self.client.login(username='admin', password='admin')

    def tearDown(self):
        calamari_rest.views.rpc_view.RPCViewSet.__init__ = self._old_init

    def assertStatus(self, response, status_code):
        self.assertEqual(response.status_code, status_code, "Bad status %s, wanted %s (%s)" % (
            response.status_code, status_code, response.data
        ))
