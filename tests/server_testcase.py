import logging
from django.utils.unittest.case import TestCase
from tests.calamari_ctl import DevCalamariControl
from tests.ceph_ctl import DevCephControl
from tests.http_client import AuthenticatedHttpClient


# TODO: make these configurable or perhaps query them
# from CalamariControl (it should know all about
# the calamari server)
API_URL = "http://localhost:8000/api/v1/"
API_USERNAME = 'admin'
API_PASSWORD = 'admin'


log = logging.getLogger(__name__)


class ServerTestCase(TestCase):
    def setUp(self):
        self.calamari_ctl = DevCalamariControl()
        self.calamari_ctl.start()

        try:
            # Calamari is up, we can login to it
            self.api = AuthenticatedHttpClient(API_URL, API_USERNAME, API_PASSWORD)
            self.api.login()

            # Let's give calamari something to monitor, though
            # it's up to the test whether they want to
            # actually fire it up/interact with it.
            self.ceph_ctl = DevCephControl()

        except:
            self.calamari_ctl.stop()
            raise

    def clear(self):
        """
        Clear down the calamari server:

        - Forget about all ceph clusters
        - Reject all minion credentials
        """
        # Initially there should be no clusters
        response = self.api.get("cluster")
        response.raise_for_status()
        for cluster in response.json():
            response = self.api.delete("cluster/%s" % cluster['id'])
            response.raise_for_status()

        # And the salt master should recognise no minions
        self.calamari_ctl.clear_keys()

    def tearDown(self):
        log.info("%s.teardown" % self.__class__.__name__)
        self.calamari_ctl.stop()
        self.ceph_ctl.shutdown()
