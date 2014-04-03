import getpass
import logging
import shutil
import tempfile
import time
import psutil
from itertools import chain
import yaml

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

    def configure(self, server_count, cluster_count=1):
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

    def mark_osd_in(self, fsid, osd_id, osd_in=True):
        raise NotImplementedError()

    def get_server_fqdns(self):
        raise NotImplementedError()

    def go_dark(self, fsid, dark=True, minion_id=None):
        """
        Create the condition where network connectivity between
        the calamari server and the ceph cluster is lost.
        """
        pass

    def get_fqdns(self, fsid):
        """
        Return all the FQDNs of machines with salt minion
        """
        raise NotImplementedError()


class EmbeddedCephControl(CephControl):
    """
    One or more simulated ceph clusters
    """
    def __init__(self):
        self._config_dirs = {}
        self._sims = {}

    def configure(self, server_count, cluster_count=1):
        osds_per_host = 4

        for i in range(0, cluster_count):
            domain = "cluster%d.com" % i
            config_dir = tempfile.mkdtemp()
            sim = MinionSim(config_dir, server_count, osds_per_host, port=8761 + i, domain=domain)
            fsid = sim.cluster.fsid
            self._config_dirs[fsid] = config_dir
            self._sims[fsid] = sim
            sim.start()

    def shutdown(self):
        log.info("%s.shutdown" % self.__class__.__name__)

        for sim in self._sims.values():
            sim.stop()
            sim.join()

        log.debug("lingering processes: %s" %
                  [p.name for p in psutil.process_iter() if p.username == getpass.getuser()])
        # Sleeps in tests suck... this one is here because the salt minion doesn't give us a nice way
        # to ensure that when we shut it down, subprocesses are complete before it returns, and even
        # so we can't be sure that messages from a dead minion aren't still winding their way
        # to cthulhu after this point.  So we fudge it.
        time.sleep(5)

        for config_dir in self._config_dirs.values():
            shutil.rmtree(config_dir)

    def get_server_fqdns(self):
        return list(chain(*[s.get_minion_fqdns() for s in self._sims.values()]))

    def mark_osd_in(self, fsid, osd_id, osd_in=True):
        self._sims[fsid].cluster.set_osd_state(osd_id, osd_in=1 if osd_in else 0)

    def go_dark(self, fsid, dark=True, minion_id=None):
        if minion_id:
            if dark:
                self._sims[fsid].halt_minion(minion_id)
            else:
                self._sims[fsid].start_minion(minion_id)
        else:
            if dark:
                self._sims[fsid].halt_minions()
            else:
                self._sims[fsid].start_minions()

        # Sleeps in tests suck... this one is here because the salt minion doesn't give us a nice way
        # to ensure that when we shut it down, subprocesses are complete before it returns, and even
        # so we can't be sure that messages from a dead minion aren't still winding their way
        # to cthulhu after this point.  So we fudge it.
        time.sleep(5)

    def get_fqdns(self, fsid):
        return self._sims[fsid].get_minion_fqdns()

    def get_service_fqdns(self, fsid, service_type):
        return self._sims[fsid].cluster.get_service_fqdns(service_type)


class ExternalCephControl(CephControl):

    def __init__(self):
        self.config = yaml.load("""
roles:
- - mon.0
  - osd.0
  - client.0
- - mon.1
  - osd.1
- - mon.2
  - osd.3
targets:
  ubuntu@mira068.front.sepia.ceph.com: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3trHqdv6rH+c81Cd2k35xKqjsnOZVUrwbbwsdBn4bAgYRqJR3MZ1D4uKzDkek86n+Q6jp7k4iZw/p3zdbPgaaFvfYVULFXnx/9QVj2VlFiJ1ly+MdF6B9qVBkgm7rm1qDRnbASUF5RXG6eSIYo6DgmVWklMtanwhhJidOWuu8RdmG/+L4d36somECVjR169Mi/m2q5T+keFIOY9d2uECVGsOjKrPB7eIkHTaNsNljhv9rb/TIAsSQB/+hxQeMl1Lko9idj4MFw6Tpy9FX+84GhpG4x99HGHRc0Xq98PqpCI3zZTW2hg58fSj2fPdk1XFXMCdrXvyQm4txJiWJba1b
  ubuntu@mira074.front.sepia.ceph.com: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDkSvRvsY0kOqz6VQHsuxO3PiGfu+p2oIjkokTymVQQhc6w/GuSUqP+73+NTQkVCaIAs3dKASpW2mcN4JlNYQadY3uzQ97hOr5GsIjpMTqKsbw9//VinLU+v2AY3vSpoKXlQ3EYMMcm/Ga4av5X2YjfyeOjMpJ7Tz2tPtTHslzXcPaY71CZc7/unsBtLXz00A/D4M87A+W70W8iNbe/ZQwZYK3PBo8EeQjhz8vyZ4mzBHbvgc1BBjuphNZSxGUqnRlU4cvm8fTgja7mAsonnYJOsw6TVr68B92Olpm7AhkRP1IFUBV9vMEqifepkSW33Gw0At+iGLAw/6yE62o3bSBx
  ubuntu@mira080.front.sepia.ceph.com: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDr6YpR1nLa5+vYU6efXaAj40U7KPAZf57z0Su2IIwVl0nR3o6nbatmkvqznAj6QuKsjgkdeWmkI/8+EnmjwJyREW6QVKk5Mrl02Lo3soS1cIrUta/ap89rWkLyd27hcYOP+DroqA9j+UbP0kKmgalsKXPOwhGlCYZJcaX7pw/m0MsiBYZ6gKtyMbyIJxu/V4TNK95zlmTr2kxy1j8GXsitNlQEGTAMy0fTnXUJpa9S1jgHVwl4DHF0loeqIpXiapE4Q4lXfrRvIxc2raPv5XYSjmVN070bmFfnQYfr8Ao4XbcPJHlNERkaGoBQ0GVCvnzV21NKc11/rp3NzC3ct1Sv
tasks:
- internal.lock_machines:
  - 3
  - mira
- internal.save_config: null
- internal.check_lock: null
- internal.connect: null
- internal.check_conflict: null
- internal.check_ceph_data: null
- internal.vm_setup: null
- internal.base: null
- internal.archive: null
- internal.coredump: null
- internal.sudo: null
- internal.syslog: null
- internal.timer: null
- ssh_keys: null
- ceph-deploy:
    branch:
      stable: dumpling
- interactive: null
""")
        # Here we will want to parse the config.yaml(s)


    def configure(self, server_count, cluster_count=1):
        # I hope you only wanted three, because I ain't buying
        # any more servers...
        assert server_count == 3
        assert cluster_count == 1

        # Ensure all OSDs are initially up: assertion per #7813

        # Ensure there are initially no pools but the default ones. assertion per #7813

        # wait till all PGs are active and clean assertion per #7813

        # bootstrap salt minions on cluster
        # TODO is the right place for it

        # set config dirs
        # set sims

    def get_server_fqdns(self):
        return [target.split('@')[1] for target in self.config['targets'].iterkeys()]

    def get_service_fqdns(self, fsid, service_type):
        # I run OSDs and mons in the same places (on all three servers)
        return self.get_server_fqdns()

    def shutdown(self):
        pass

    def get_fqdns(self, fsid):
        # TODO when we support multiple cluster change this
        return self.get_server_fqdns()

    def go_dark(self, fsid, dark=True, minion_id=None):
        pass

    def mark_osd_in(self, fsid, osd_id, osd_in=True):
        pass


if __name__ == "__main__":
    externalctl = ExternalCephControl()
    assert isinstance(externalctl.config, dict)
    import pdb; pdb.set_trace()