import logging
from django.utils.unittest.case import TestCase
from tests.calamari_ctl import EmbeddedCalamariControl, ExternalCalamariControl
from tests.ceph_ctl import EmbeddedCephControl, ExternalCephControl


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


if True:
    CALAMARI_CTL = EmbeddedCalamariControl
    CEPH_CTL = EmbeddedCephControl
else:
    # TODO: config file or something to allow selecting mode
    CALAMARI_CTL = ExternalCalamariControl
    CEPH_CTL = ExternalCephControl


class ServerTestCase(TestCase):
    def setUp(self):
        self.calamari_ctl = CALAMARI_CTL()

        try:
            self.calamari_ctl.start()

            self.api = self.calamari_ctl.api

            # Let's give calamari something to monitor, though
            # it's up to the test whether they want to
            # actually fire it up/interact with it.
            self.ceph_ctl = CEPH_CTL()

        except:
            log.exception("Exception during setup, tearing down")
            self.calamari_ctl.stop()
            raise

    def tearDown(self):
        log.info("%s.teardown" % self.__class__.__name__)
        # Prefer to shut down ceph cluster first, otherwise minions go through
        # a confusing "I can't reach my master" phase rather than a nice smooth
        # shutdown.
        self.ceph_ctl.shutdown()
        self.calamari_ctl.stop()

    def _wait_for_cluster(self, cluster_count=1):
        """
        Return an ID if cluster_count is 1, else return a list of IDs.
        """
        self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())
        log.debug("Authorized keys")

        wait_until_true(lambda: self._cluster_detected(cluster_count), timeout=HEARTBEAT_INTERVAL * 3)
        log.debug("Detected cluster")

        if cluster_count == 1:
            cluster_id = self.api.get("cluster").json()[0]['id']
            wait_until_true(lambda: self._maps_populated(cluster_id))
            return cluster_id
        else:
            result = []
            for cluster in self.api.get("cluster").json():
                wait_until_true(lambda: self._maps_populated(cluster['id']))
                result.append(cluster['id'])
            return result

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
