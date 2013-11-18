from django.utils.unittest.case import skipIf
import time
from tests.server_testcase import ServerTestCase
from tests.utils import wait_until_true, WaitTimeout


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


class TestMonitoring(ServerTestCase):
    def test_detect_simple(self):
        """
        Check that a single cluster, when sending a heartbeat to the
        calamari server, becomes visible via the REST API
        """
        self._wait_for_cluster()

        # TODO: validate what is reported by the REST API against
        # what is known about the cluster from CephControl

    def test_osd_out(self):
        """
        Check Calamari's reaction to an OSD going down:

        - The OSD map should be updated
        - The health information should be updated and indicate a warning
        """

        cluster_id = self._wait_for_cluster()

        # Pick an OSD and check its initial status
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
        # NB this is actually a bit racy, because we assume the PGs remain degraded long enough
        # to affect the health state: in theory they could all get remapped instantaneously, in
        # which case the cluster would never appear unhealthy and this would be an invalid check.
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

    def test_cluster_down(self):
        """
        Check Calamari's reaction to total loss of contact with
        a Ceph cluster being monitored.

        - The cluster update time should stop getting incremented
        - The system should recover promptly when the cluster comes
          back online.
        """
        cluster_id = self._wait_for_cluster()

        def update_time():
            return self.api.get("cluster/%s" % cluster_id).json()['cluster_update_time']

        # Lose contact with the cluster
        self.ceph_ctl.go_dark()
        initial_update_time = update_time()
        time.sleep(HEARTBEAT_INTERVAL * 3)
        # The update time should not have been incremented
        self.assertEqual(initial_update_time, update_time())

        # Regain contact with the cluster
        self.ceph_ctl.go_dark(False)
        # The update time should start incrementing again
        wait_until_true(lambda: update_time() != initial_update_time, timeout=HEARTBEAT_INTERVAL * 3)
        self.assertNotEqual(initial_update_time, update_time())

    def test_mon_down(self):
        """
        Check Calamari's reaction to loss of contact with
        individual mon servers in a Ceph cluster.

        - The cluster state should continue to be updated
          as long as there is a mon quorum and
          one mon is available to calamari.
        """
        cluster_id = self._wait_for_cluster()
        mon_fqdns = self.ceph_ctl.get_service_fqdns('mon')

        def update_time():
            return self.api.get("cluster/%s" % cluster_id).json()['cluster_update_time']

        # I don't know which if any of the mons the calamari server
        # might be preferentially accepting data from, but I want
        # to ensure that it can survive any of them going away.
        for mon_fqdn in mon_fqdns:
            self.ceph_ctl.go_dark(minion_id=mon_fqdn)
            last_update_time = update_time()

            # This will give a timeout exception if calamari did not
            # re establish monitoring after the mon server went offline.
            try:
                wait_until_true(lambda: last_update_time != update_time(), timeout=CALAMARI_RESYNC_PERIOD)
            except WaitTimeout:
                self.fail("Failed to recover from killing %s in %s seconds" % (
                    mon_fqdn, CALAMARI_RESYNC_PERIOD))

            self.ceph_ctl.go_dark(dark=False, minion_id=mon_fqdn)

    def _wait_for_cluster(self):
        self.clear()
        self.ceph_ctl.configure(3)
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

