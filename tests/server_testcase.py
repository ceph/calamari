import logging
from django.utils.unittest.case import TestCase
from tests.calamari_ctl import EmbeddedCalamariControl, ExternalCalamariControl
from tests.ceph_ctl import EmbeddedCephControl, ExternalCephControl


from tests.utils import scalable_wait_until_true

from tests.config import TestConfig

config = TestConfig()

logging.basicConfig()
log = logging.getLogger(__name__)


# Roughly how long should it take for one OSD to
# recover its PGs after an outage?  This is a 'finger in the air'
# number that depends on the ceph cluster used in testing.  It's
# how long you should wait calamari to report a cluster healthy
# after you've cycled an OSD in-out-in.
OSD_RECOVERY_PERIOD = 600


# This is the latency for a command to run and then for the
# resulting OSD map to get synced up to the calamari server
REQUEST_TIMEOUT = 20


if config.get('testing', 'calamari_control') == 'embedded':
    CALAMARI_CTL = EmbeddedCalamariControl
elif config.get('testing', 'calamari_control') == 'external':
    CALAMARI_CTL = ExternalCalamariControl
else:
    raise NotImplementedError()

if config.get('testing', 'ceph_control') == 'embedded':
    CEPH_CTL = EmbeddedCephControl
elif config.get('testing', 'ceph_control') in ('external', 'converged'):
    CEPH_CTL = ExternalCephControl
else:
    raise NotImplementedError()


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

        except Exception:
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

        # Once I've authorized the keys, the first mon to retry its salt authentication
        # will cause the cluster to get noticed.
        salt_auth_retry_interval = 10

        scalable_wait_until_true(lambda: self._cluster_detected(cluster_count), timeout=salt_auth_retry_interval * 2)
        log.debug("Detected cluster")

        if cluster_count == 1:
            cluster_id = self.api.get("cluster").json()[0]['id']
            scalable_wait_until_true(lambda: self._maps_populated(cluster_id))
            return cluster_id
        else:
            result = []
            for cluster in self.api.get("cluster").json():
                scalable_wait_until_true(lambda: self._maps_populated(cluster['id']))
                result.append(cluster['id'])
            return result

    def _wait_for_servers(self):
        """
        Wait for all the expected servers to appear in the REST API
        """
        expected_servers = set(self.ceph_ctl.get_server_fqdns())

        def servers_available():
            servers = self.api.get("server").json()
            managed_servers = [s for s in servers if s['managed']]
            ready = set([s['fqdn'] for s in managed_servers]) == expected_servers
            if not ready:
                log.debug("_wait_for_servers: {0} ({1} managed) servers visible vs. {2} expected".format(
                    len(servers), len(managed_servers), len(expected_servers)
                ))
            return ready

        scalable_wait_until_true(servers_available, timeout=30)

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
        """
        Check that Calmari server has got all the data for a cluster, as well
        as just knowing the cluster exists.
        """
        any_absent = False
        for url in ["cluster/{0}/osd", "cluster/{0}/config", "cluster/{0}/server"]:
            response = self.api.get(url.format(cluster_id))
            if response.status_code == 500:
                response.raise_for_status()
            if response.status_code != 200 or not len(response.json()):
                any_absent = True
                break

        return not any_absent

    def assert_status(self, response, status_code):
        self.assertEqual(response.status_code, status_code, "Bad status %s, wanted %s (%s)" % (
            response.status_code, status_code, response.content
        ))


class RequestTestCase(ServerTestCase):
    """
    For test cases that need to deal with running requests
    """
    def _request_complete(self, request_id, check):
        """
        Return whether a request has completed successfully.
        If the request has failed, raise an exception.
        """
        r = self.api.get("request/%s" % request_id)
        r.raise_for_status()

        if check and r.json()['error']:
            raise self.failureException("Request %s failed: %s" % (request_id, r.json()['error_message']))

        return r.json()['state'] == 'complete'

    def _wait_for_completion(self, response, timeout=None):
        """
        Wait for a user request to complete successfully, given the response from a PATCH/POST/DELETE
        """
        if timeout is None:
            timeout = REQUEST_TIMEOUT
        self.assertEqual(response.status_code, 202)
        request_id = response.json()['request_id']
        self._wait_for_request(request_id, timeout)

    def _wait_for_request(self, request_id, timeout=None, check=True):
        """
        :param check: If true, we raise an exception on requests that fail
        """
        scalable_wait_until_true(lambda: self._request_complete(request_id, check=check), timeout=timeout)
