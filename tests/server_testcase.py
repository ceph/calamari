import logging
from django.utils.unittest.case import TestCase
from requests import ConnectionError
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
# sane upper bounds on wait.

# This is how long you should wait if you're waiting
# for something to happen roughly 'on the next heartbeat'.
HEARTBEAT_INTERVAL = 120

# How long should calamari take to re-establish
# sync after a mon goes down?
CALAMARI_RESYNC_PERIOD = HEARTBEAT_INTERVAL * 2

# Roughly how long should it take for one OSD to
# recover its PGs after an outage?  This is a 'finger in the air'
# number that depends on the ceph cluster used in testing.  It's
# how long you should wait calamari to report a cluster healthy
# after you've cycled an OSD in-out-in.
OSD_RECOVERY_PERIOD = 600


CALAMARI_CTL = EmbeddedCalamariControl
CEPH_CTL = EmbeddedCephControl
FORCE_KEYS = True


class ServerTestCase(TestCase):

    def _api_connectable(self):
        """
        Return true if we can complete an HTTP request without
        raising ConnectionError.
        """
        try:
            self.api.get("auth/login/")
        except ConnectionError:
            return False
        else:
            return True

    def setUp(self):
        self.calamari_ctl = CALAMARI_CTL()
        self.calamari_ctl.start()

        try:
            self.api = self.calamari_ctl.api

            # The calamari REST API goes through a brief period between process
            # startup and servicing connections
            wait_until_true(self._api_connectable)

            # Calamari REST API will return 503s until the backend is fully up
            # and responding to ZeroRPC requests.
            wait_until_true(lambda: self.api.get("cluster").status_code != 503, timeout=30)

            # Let's give calamari something to monitor, though
            # it's up to the test whether they want to
            # actually fire it up/interact with it.
            self.ceph_ctl = CEPH_CTL()

            # Bit awkward, if this is a simulated ceph cluster then it will
            # probably reuse some domain names and we want to make sure
            # that calamari doesn't have any keys kicking around.
            if isinstance(self.ceph_ctl, EmbeddedCephControl):
                self.calamari_ctl.clear_keys()

        except:
            self.calamari_ctl.stop()
            raise

    def tearDown(self):
        log.info("%s.teardown" % self.__class__.__name__)
        # Prefer to shut down ceph cluster first, otherwise minions go through
        # a confusing "I can't reach my master" phase rather than a nice smooth
        # shutdown.
        self.ceph_ctl.shutdown()
        self.calamari_ctl.stop()

    def _wait_for_cluster(self):
        if FORCE_KEYS:
            self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())
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
