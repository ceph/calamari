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
        Tell me about the kind of system you would like.

        We will give you that system in a clean state or not at all:
        - Sometimes by setting it up for you here and now
        - Sometimes by cleaning up an existing cluster that's left from a previous test
        - Sometimes a clean cluster is already present for us
        - Sometimes we may not be able to give you the configuration you asked for
          (maybe you asked for more servers than we have servers) and have to
          throw you a test skip exception
        - Sometimes we may have a cluster that we can't clean up well enough
          to hand back to you, and have to throw you an error exception
        """
        raise NotImplementedError()

    def shutdown(self):
        """
        This cluster will not be used further by the test.

        If you created a cluster just for the test, tear it down here.  If the
        cluster was already up, just stop talking to it.
        """
        raise NotImplementedError()

    def mark_osd_in(self, osd_id, osd_in=True):
        raise NotImplementedError()

    def get_server_fqdns(self):
        raise NotImplementedError()

    def go_dark(self, dark=True):
        """
        Emulate the condition where network connectivity between
        the calamari server and the ceph cluster is lost.
        """
        pass


class EmbeddedCephControl(CephControl):
    """
    Simulated ceph cluster, using minion_sim
    """
    def __init__(self):
        self._config_dir = tempfile.mkdtemp()
        self._sim = None

    def configure(self, server_count):
        self._sim = MinionSim(self._config_dir, server_count)
        self._sim.start()

    def shutdown(self):
        log.info("%s.shutdown" % self.__class__.__name__)

        if self._sim:
            self._sim.stop()
            self._sim.join()
        shutil.rmtree(self._config_dir)

    def get_server_fqdns(self):
        return self._sim.get_minion_fqdns()

    def mark_osd_in(self, osd_id, osd_in=True):
        self._sim.cluster.set_osd_state(osd_id, osd_in=1 if osd_in else 0)

    def go_dark(self, dark=True, minion_id=None):
        if minion_id:
            if dark:
                self._sim.halt_minion(minion_id)
            else:
                self._sim.start_minion(minion_id)
        else:
            if dark:
                self._sim.halt_minions()
            else:
                self._sim.start_minions()

    def get_service_fqdns(self, service_type):
        return self._sim.cluster.get_service_fqdns(service_type)


class ExternalCephControl(CephControl):
    def configure(self, server_count):
        # I hope you only wanted three, because I ain't buying
        # any more servers...
        assert server_count == 3

        # Ensure all OSDs are initially up

        # Ensure there are initially no pools but the default ones.

    def get_server_fqdns(self):
        return ["gravel%s.rockery" % n for n in range(0, 3)]

    def get_service_fqdns(self, service_type):
        # I run OSDs and mons in the same places (on all three servers)
        return self.get_server_fqdns()

    def shutdown(self):
        pass
