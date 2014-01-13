from ConfigParser import ConfigParser
import logging
import os
import socket
import subprocess
import xmlrpclib
import signal
import errno
from requests import ConnectionError
from tests.http_client import AuthenticatedHttpClient
from tests.utils import wait_until_true, WaitTimeout

log = logging.getLogger(__name__)

# Assumes running nosetests from root of git repo
TREE_ROOT = os.path.abspath("./")

API_URL = "http://localhost:8000/api/v2/"
API_USERNAME = 'admin'
API_PASSWORD = 'admin'


# We scale this linearly with the number of fqdns expected
KEY_WAIT_PERIOD = 3


class CalamariControl(object):
    """
    Interface for tests to control the Calamari server under test.

    This can either be controlling a development mode instance running
    as an unprivileged user right here with the tests, or a full production
    installation running on a dedicated host.
    """

    def __init__(self):
        log.info("CalamariControl.__init__")
        self._api = None

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    @property
    def api_url(self):
        return API_URL

    @property
    def api_username(self):
        return API_USERNAME

    @property
    def api_password(self):
        return API_PASSWORD

    @property
    def api(self):
        if self._api is None:
            log.info("Initializing API")
            api = AuthenticatedHttpClient(
                self.api_url,
                self.api_username,
                self.api_password)
            api.login()
            self._api = api

        return self._api

    def clear_keys(self):
        r_keys = self.api.get("key")
        r_keys.raise_for_status()
        for key in r_keys.json():
            r = self.api.delete("key/%s" % key['id'])
            r.raise_for_status()

    def authorize_keys(self, minion_ids):
        def _fqdns_present():
            found_ids = [m['id'] for m in self.api.get("key").json()]
            all_present = len(set(minion_ids) & set(found_ids)) == len(minion_ids)

            log.debug("checking keys, looking for %s found %s (%s)" % (minion_ids, found_ids, all_present))

            return all_present

        wait_until_true(_fqdns_present, timeout=KEY_WAIT_PERIOD * len(minion_ids))

        for minion_id in minion_ids:
            log.debug("Authorising key for %s" % minion_id)
            r = self.api.patch("key/%s" % minion_id, {'status': 'accepted'})
            r.raise_for_status()

    def configure(self, no_clusters=True):
        """
        Assert some aspects of the server state, fixing up
        if possible, else raising an exception.

        Tests call this to say "I need calamari to be
        up and running" or "I need calamari to be offline
        initially" or "I need calamari to initially have
        no clusters" or "I need calamari to initially have
        no pools".

        The idea is that tests generally can
        be quite liberal about the starting state of
        the system, but specific about the things that
        will affect the validity of their checks.

        A badly behaved calamari instance can break this: the only
        way to get around that is to provision a fully fresh instance
        for each test.
        """

        if no_clusters:
            # Initially there should be no clusters
            response = self.api.get("cluster")
            response.raise_for_status()
            for cluster in response.json():
                response = self.api.delete("cluster/%s" % cluster['id'])
                response.raise_for_status()


class EmbeddedCalamariControl(CalamariControl):
    """
    Runs a dev-mode calamari server by invoking supervisord directly
    """
    def __init__(self):
        super(EmbeddedCalamariControl, self).__init__()
        self._ps = None
        self._rpc = None

    def _available(self):
        try:
            status = self._rpc.supervisor.getState()
            return status['statename'] == 'RUNNING'
        except socket.error:
            return False
        except xmlrpclib.Fault:
            raise

    def _services_up(self):
        ps_info = self._rpc.supervisor.getAllProcessInfo()
        if not ps_info:
            return False

        up = True
        for ps in ps_info:
            if ps['statename'] != 'RUNNING':
                up = False
                log.debug("Service %s not up yet" % ps['group'])

        if up:
            log.info("All services running: %s" % [p['group'] for p in ps_info])

        return up

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

    def restart(self):
        processes = [ps['group'] for ps in self._rpc.supervisor.getAllProcessInfo()]
        for ps in processes:
            self._rpc.supervisor.stopProcessGroup(ps)
        for ps in processes:
            self._rpc.supervisor.startProcessGroup(ps)
        wait_until_true(self._services_up)

    def start(self):
        config_path = os.path.join(TREE_ROOT, "dev/supervisord.conf")
        assert os.path.exists(config_path)
        self._ps = subprocess.Popen(
            ["supervisord", "-n", "-c", config_path],
            cwd=os.path.abspath(TREE_ROOT),
            stdout=open("supervisord.out.log", 'w'),
            stderr=open("supervisord.err.log", 'w')
        )
        if not self._ps:
            raise RuntimeError("Failed to launch supervisor")

        config = ConfigParser()
        config.read(config_path)
        xmlrpc_addr = config.get('inet_http_server', 'port')
        self._rpc = xmlrpclib.ServerProxy("http://%s/RPC2" % xmlrpc_addr)

        try:
            # Wait for supervisor to start responding to RPC
            wait_until_true(self._available)

            # Wait for all supervisor's children to start
            wait_until_true(self._services_up)
        except:
            # Ensure that failures during startup do not leave a
            # zombie supervisor process
            log.error("Exception during setup, killing supervisor")
            self._ps.send_signal(signal.SIGINT)
            try:
                wait_until_true(lambda: self._ps.poll() is not None)
            except WaitTimeout:
                log.error("Supervisor isn't dying, sending it KILL")
                self._ps.send_signal(signal.SIGKILL)
            self._ps.wait()
            raise

        # The calamari REST API goes through a brief period between process
        # startup and servicing connections
        wait_until_true(self._api_connectable)

        # Calamari REST API will return 503s until the backend is fully up
        # and responding to ZeroRPC requests.
        wait_until_true(lambda: self.api.get("cluster").status_code != 503, timeout=30)

        # Because we are embedded, we should act like a fresh instance
        # and not let any old keys linger
        self.clear_keys()

    def stop(self):
        log.info("%s.stop" % self.__class__.__name__)
        if self._ps:
            try:
                self._ps.send_signal(signal.SIGINT)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    return
                else:
                    raise
            else:
                stdout, stderr = self._ps.communicate()
                rc = self._ps.wait()
                if rc != 0:
                    raise RuntimeError("supervisord did not terminate cleanly: %s %s %s" % (rc, stdout, stderr))


class ExternalCalamariControl(CalamariControl):
    """
    Already got a calamari instance running, and you want to point
    the tests at that?  Use this class.
    """
    def start(self):
        pass

    def stop(self):
        pass
