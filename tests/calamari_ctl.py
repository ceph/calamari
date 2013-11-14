from ConfigParser import ConfigParser
import logging
import os
import socket
import subprocess
import xmlrpclib
import signal
from tests.utils import wait_until_true, WaitTimeout

log = logging.getLogger(__name__)

# Assumes running nosetests from root of git repo
TREE_ROOT = os.path.abspath("./")


class CalamariControl(object):
    """
    Interface for tests to control the Calamari server under test.

    This can either be controlling a development mode instance running
    as an unprivileged user right here with the tests, or a full production
    installation running on a dedicated host.
    """

    def start(self):
        raise NotImplementedError()


class DevCalamariControl(object):
    """
    Runs a dev-mode calamari server by invoking supervisord directly
    """
    def __init__(self):
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

    def start(self):
        config_path = os.path.join(TREE_ROOT, "supervisord.conf")
        assert os.path.exists(config_path)
        self._ps = subprocess.Popen(
            ["supervisord", "-n", "-c", config_path],
            cwd=os.path.abspath(TREE_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
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

    def stop(self):
        self._ps.send_signal(signal.SIGINT)
        stdout, stderr = self._ps.communicate()
        rc = self._ps.wait()
        if rc != 0:
            raise RuntimeError("supervisord did not terminate cleanly: %s %s %s" % (rc, stdout, stderr))
