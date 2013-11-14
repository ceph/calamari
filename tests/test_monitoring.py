
import logging
from django.utils.unittest import TestCase
from tests.calamari_ctl import DevCalamariControl
from tests.http_client import AuthenticatedHttpClient


API_URL = "http://localhost:8000/api/v1/"
API_USERNAME = 'admin'
API_PASSWORD = 'admin'

log = logging.getLogger(__name__)


class TestMonitoring(TestCase):
    def setUp(self):
        self.calamarictl = DevCalamariControl()
        self.calamarictl.start()

        try:
            # Calamari is up, we can login to it
            self.api = AuthenticatedHttpClient(API_URL, API_USERNAME, API_PASSWORD)
            self.api.login()
        except:
            self.calamarictl.stop()
            raise

    def test_detect_simple(self):
        """
        Check that a single cluster, when sending a heartbeat to the
        calamari server, becomes visible via the REST API
        """

        # Start Calamari

        # Start Ceph

        # Wait up to 3x heartbeat interval for the Ceph cluster to appear in the

    def tearDown(self):
        self.calamarictl.stop()
