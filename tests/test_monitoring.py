
import logging
from django.utils.unittest import TestCase
from tests.calamari_ctl import DevCalamariControl
from tests.ceph_ctl import DevCephControl
from tests.http_client import AuthenticatedHttpClient
from tests.utils import wait_until_true


API_URL = "http://localhost:8000/api/v1/"
API_USERNAME = 'admin'
API_PASSWORD = 'admin'

log = logging.getLogger(__name__)


class TestMonitoring(TestCase):
    def setUp(self):
        self.calamari_ctl = DevCalamariControl()
        self.calamari_ctl.start()

        try:
            # Calamari is up, we can login to it
            self.api = AuthenticatedHttpClient(API_URL, API_USERNAME, API_PASSWORD)
            self.api.login()

            # Let's give calamari something to monitor
            self.ceph_ctl = DevCephControl()

        except:
            self.calamari_ctl.stop()
            raise

    def test_detect_simple(self):
        """
        Check that a single cluster, when sending a heartbeat to the
        calamari server, becomes visible via the REST API
        """

        # Initially there should be no clusters
        response = self.api.get("cluster")
        response.raise_for_status()
        for cluster in response.json():
            response = self.api.delete("cluster/%s" % cluster['id'])
            response.raise_for_status()

        # And the salt master should recognise no minions
        self.calamari_ctl.clear_keys()

        # Then we start up our Ceph Cluster
        self.ceph_ctl.configure(3)
        self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())

        def cluster_detected():
            response = self.api.get("cluster")
            response.raise_for_status()
            return bool(response.json())

        wait_until_true(cluster_detected)

    def tearDown(self):
        log.info("%s.teardown" % self.__class__.__name__)
        self.ceph_ctl.shutdown()
        self.calamari_ctl.stop()
