from django.utils.unittest.case import skipIf
from tests.server_testcase import ServerTestCase
from tests.utils import wait_until_true


# The tests need to have a rough idea of how often
# calamari checks things, so that they can set
# sane upper bounds on waits
HEARTBEAT_INTERVAL = 10

# Roughly how long should it take for one OSD to
# recover its PGs after an outage?  This is a 'finger in the air'
# number that depends on the ceph cluster used in testing.
OSD_RECOVERY_PERIOD = 600


class TestMonitoring(ServerTestCase):
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

    def test_detect_simple(self):
        """
        Check that a single cluster, when sending a heartbeat to the
        calamari server, becomes visible via the REST API
        """
        self.clear()

        # Start one Ceph cluster
        self.ceph_ctl.configure(3)
        # Authorize the Ceph servers' minions
        self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())

        # Check that the Ceph cluster appears in the REST API
        wait_until_true(self._cluster_detected, timeout=HEARTBEAT_INTERVAL*3)

    @skipIf(True, "Not implemented yet")
    def test_cluster_down(self):
        """
        Check Calamari's reaction to total loss of contact with
        a Ceph cluster being monitored.

        - The cluster update time should stop getting incremented
        - TODO an alert should be recorded
        - The system should recover promptly when the cluster comes
          back online.
        """
        pass

    @skipIf(True, "Not implemented yet")
    def test_mon_down(self):
        """
        Check Calamari's reaction to loss of contact with
        individual mon servers in a Ceph cluster.

        - The cluster state should continue to be updated
          as long as there is a mon quorum and
          one mon is available to calamari.
        """
        pass

    def test_osd_out(self):
        """
        Check Calamari's reaction to an OSD going down:

        - The OSD map should be updated
        - The health information should be updated and indicate a warning
        - TODO an alert should be recorded
        """

        # Start monitoring a cluster
        self.clear()
        self.ceph_ctl.configure(3)
        self.calamari_ctl.authorize_keys(self.ceph_ctl.get_server_fqdns())
        wait_until_true(self._cluster_detected, timeout=HEARTBEAT_INTERVAL*3)

        # Pick an OSD and check its initial status
        cluster_id = self.api.get("cluster").json()[0]['id']
        wait_until_true(lambda: self._maps_populated(cluster_id))
        osd_id = 0
        osd_url = "cluster/{0}/osd/{1}".format(cluster_id, osd_id)

        # Check it's initially up and in
        initial_osd_status = self.api.get(osd_url).json()['osd']
        self.assertEqual(initial_osd_status['up'], 1)
        self.assertEqual(initial_osd_status['in'], 1)

        # Cause it to 'spontaneously' (as far as calamari is concerned)
        # be marked out
        self.ceph_ctl.mark_osd_in(osd_id, False)

        # Wait for the status to filter up to the REST API
        wait_until_true(lambda: self.api.get(osd_url).json()['osd']['in'] == 0,
                        timeout=HEARTBEAT_INTERVAL*3)

        # Wait for the health status to reflect the degradation
        health_url = "cluster/{0}/health".format(cluster_id)
        wait_until_true(lambda: self.api.get(health_url).json()['report']['overall_status'] == "HEALTH_WARN",
                        timeout=HEARTBEAT_INTERVAL*3)

        # Bring the OSD back into the cluster
        self.ceph_ctl.mark_osd_in(osd_id, True)

        # Wait for the status
        wait_until_true(lambda: self.api.get(osd_url).json()['osd']['in'] == 1, timeout=HEARTBEAT_INTERVAL*3)

        # Wait for the health
        # This can take a long time, because it has to wait for PGs to fully recover
        wait_until_true(lambda: self.api.get(health_url).json()['report']['overall_status'] == "HEALTH_OK",
                        timeout=OSD_RECOVERY_PERIOD*2)
