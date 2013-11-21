from django.utils.unittest.case import skipIf
import time
from tests.server_testcase import ServerTestCase, HEARTBEAT_INTERVAL, OSD_RECOVERY_PERIOD, CALAMARI_RESYNC_PERIOD
from tests.utils import wait_until_true, WaitTimeout


class TestMonitoring(ServerTestCase):
    def setUp(self):
        super(TestMonitoring, self).setUp()
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()

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
                        timeout=HEARTBEAT_INTERVAL)

        # Wait for the health status to reflect the degradation
        # NB this is actually a bit racy, because we assume the PGs remain degraded long enough
        # to affect the health state: in theory they could all get remapped instantaneously, in
        # which case the cluster would never appear unhealthy and this would be an invalid check.
        health_url = "cluster/{0}/health".format(cluster_id)
        wait_until_true(lambda: self.api.get(health_url).json()['report']['overall_status'] == "HEALTH_WARN",
                        timeout=HEARTBEAT_INTERVAL)

        # Bring the OSD back into the cluster
        self.ceph_ctl.mark_osd_in(osd_id, True)

        # Wait for the status
        wait_until_true(lambda: self.api.get(osd_url).json()['osd']['in'] == 1, timeout=HEARTBEAT_INTERVAL)

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
            return self.api.get("cluster/%s" % cluster_id).json()['update_time']

        # Lose contact with the cluster
        self.ceph_ctl.go_dark()
        initial_update_time = update_time()
        time.sleep(HEARTBEAT_INTERVAL)
        # The update time should not have been incremented
        self.assertEqual(initial_update_time, update_time())

        # Regain contact with the cluster
        self.ceph_ctl.go_dark(False)
        # The update time should start incrementing again
        wait_until_true(lambda: update_time() != initial_update_time, timeout=HEARTBEAT_INTERVAL)
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
            return self.api.get("cluster/%s" % cluster_id).json()['update_time']

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

    @skipIf(True, "not implemented yet")
    def test_recovery(self):
        """
        Check that calamari persists enough data about the monitored cluster
        that it can service REST API read operations even if it restarts
        while the cluster is unavailable.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_two_clusters(self):
        """
        Check that if two ceph clusters are talking to the calamari server,
        then both are detected, and each one is presenting its own data
        via the REST API.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_cluster_removal(self):
        """
        Check that if a cluster stops communicating with calamari server,
        and we request for the cluster to be removed, it goes away.
        """
        pass
