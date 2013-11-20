import logging
from django.utils.unittest.case import TestCase
from tests.calamari_ctl import EmbeddedCalamariControl, ExternalCalamariControl
from tests.ceph_ctl import EmbeddedCephControl, ExternalCephControl
from tests.http_client import AuthenticatedHttpClient


# TODO: make these configurable or perhaps query them
# from CalamariControl (it should know all about
# the calamari server)
from tests.utils import wait_until_true


log = logging.getLogger(__name__)


# The tests need to have a rough idea of how often
# calamari checks things, so that they can set
# sane upper bounds on waits
HEARTBEAT_INTERVAL = 120

# How long should calamari take to re-establish
# sync after a mon goes down?
CALAMARI_RESYNC_PERIOD = HEARTBEAT_INTERVAL * 6

# Roughly how long should it take for one OSD to
# recover its PGs after an outage?  This is a 'finger in the air'
# number that depends on the ceph cluster used in testing.
OSD_RECOVERY_PERIOD = 600


class ServerTestCase(TestCase):
    def setUp(self):
        self.calamari_ctl = ExternalCalamariControl()
        self.calamari_ctl.start()

        try:
            self.api = self.calamari_ctl.api

            # Calamari REST API will return 503s until the backend is fully up
            # and responding to ZeroRPC requests.
            wait_until_true(lambda: self.api.get("cluster").status_code != 503, timeout=30)

            # Let's give calamari something to monitor, though
            # it's up to the test whether they want to
            # actually fire it up/interact with it.
            self.ceph_ctl = ExternalCephControl()

        except:
            self.calamari_ctl.stop()
            raise

    def tearDown(self):
        log.info("%s.teardown" % self.__class__.__name__)
        self.calamari_ctl.stop()
        self.ceph_ctl.shutdown()

    def _wait_for_cluster(self):
        #self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())
        wait_until_true(self._cluster_detected, timeout=HEARTBEAT_INTERVAL*3)
        cluster_id = self.api.get("cluster").json()[0]['id']
        wait_until_true(lambda: self._maps_populated(cluster_id))
        return cluster_id

    def _cluster_detected(self, expected=1):
        response = self.api.get("cluster")
        response.raise_for_status()
        clusters = response.json()
        if len(clusters) < expected:
            return False
        elif len(clusters) == expected:
            return True
        else:
            raise self.failureException("Too many clusters: %s" % clusters)

    def _maps_populated(self, cluster_id):
        response = self.api.get("cluster/{0}/osd".format(cluster_id))
        response.raise_for_status()
        osds = response.json()
        return bool(len(osds))
