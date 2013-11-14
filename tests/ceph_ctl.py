import logging
import shutil
import tempfile
from minion_sim.sim import MinionSim


log = logging.getLogger(__name__)


class CephControl(object):
    """
    Interface for tests to control one or more Ceph clusters under test.

    This can either be controlling the minion-sim, running unprivileged
    in a development environment, or it can be controlling a real life
    Ceph cluster.

    Some configuration arguments may be interpreted by a
    dev implementation as a "simulate this", while a real-cluster
    implementation might interpret them as "I require this state, skip
    the test if this cluster can't handle that".
    """

    def configure(self, server_count):
        """
        Tell me about the kind of system you would like
        """
        raise NotImplementedError()

    def mark_osd_out(self, osd_id):
        raise NotImplementedError()


class DevCephControl(CephControl):
    """
    Simulated ceph cluster, using minion_sim
    """
    def __init__(self):
        self._config_dir = None
        self._sim = None

    def configure(self, server_count):
        self._config_dir = tempfile.mkdtemp()

        self._sim = MinionSim(self._config_dir, server_count)
        self._sim.start()

    def get_server_fqdns(self):
        return self._sim.get_minion_fqdns()

    def shutdown(self):
        log.info("%s.shutdown" % self.__class__.__name__)

        if self._sim:
            self._sim.stop()
            self._sim.join()
        shutil.rmtree(self._config_dir)


class RealCephControl(CephControl):
    """
    TODO: hook into a real life ceph cluster (provisioned with teuthology?)
    """
    pass
