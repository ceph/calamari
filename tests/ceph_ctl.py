import getpass
import logging
import shutil
import tempfile
import time
import psutil
from itertools import chain
import yaml
from subprocess import Popen, PIPE
from utils import scalable_wait_until_true, run_once
import json
import urllib2

from nose.exc import SkipTest
from tests.config import TestConfig

config = TestConfig()
log = logging.getLogger("ceph_ctl")
log.setLevel(logging.DEBUG)


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

        from minion_sim.sim import MinionSim

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
    """
    This is the code that talks to a cluster. It is currently dependent on teuthology
    """

    def __init__(self):
        with open(config.get('testing', 'external_cluster_path')) as f:
            self.config = yaml.load(f)

        # TODO parse this out of the cluster.yaml
        self.cluster_name = 'ceph'
        self.default_pools = set(['data', 'metadata', 'rbd'])

        self.ceph_control = config.get('testing', 'ceph_control')

        self.cluster_distro = None
        if config.has_option('testing', 'cluster_distro'):
            self.cluster_distro = config.get('testing', 'cluster_distro')

    def _run_command(self, target, command):
        log.debug(target)
        log.debug(command)
        user_at_host = next(t for t in self.config['cluster'].iterkeys() if t.split('@')[1] == target)
        if self.ceph_control == 'converged':
            proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        elif self.ceph_control == 'external':
            proc = Popen([
                'ssh',
                '-oStrictHostKeyChecking=no',
                '-oUserKnownHostsFile=/dev/null',
                user_at_host,
                command], stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            log.error("stdout: %s" % out)
            log.error("stderr: %s" % err)
            raise RuntimeError("Error {0} running {1}:'{2}'".format(
                proc.returncode, target, command
            ))
        else:
            log.info(err)

        return out

    def configure(self, server_count, cluster_count=1):
        log.debug('external configure')
        if cluster_count != 1:
            raise SkipTest('ExternalCephControl does not do multiple clusters')

        if config.has_option('testing', 'bootstrap'):
            bootstrap = config.getboolean('testing', 'bootstrap')
        else:
            bootstrap = True

        if cluster_count != 1:
            raise SkipTest('ExternalCephControl does not do multiple clusters')

        if config.has_option('testing', 'bootstrap'):
            bootstrap = config.getboolean('testing', 'bootstrap')
        else:
            bootstrap = True

        if bootstrap:
            self._bootstrap(self.config['master_fqdn'])

        self.restart_minions()

        self.reset_crush_map()
        self.reset_all_osds(self._list_osds())

        self.reset_all_pools(self._list_pools())

        self.wait_till_osds_up_and_in()

        # Ensure there are initially no pools but the default ones. assertion per #7813
        self._wait_for_state(self._list_pools,
                             self._check_default_pools_only)

        # wait till all PGs are active and clean assertion per #7813
        self._wait_for_state(self._list_pgs,
                             self._check_pgs_active_and_clean)

    def wait_till_osds_up_and_in(self):
        # Ensure all OSDs are initially up: assertion per #7813
        self._wait_for_state(self._list_osds,
                             self._check_osds_in_and_up)

    def get_service_fqdns(self, fsid, service_type):
        fqdns = []
        for target, roles in self.config['cluster'].iteritems():
            if any([r.startswith(service_type) for r in roles['roles']]):
                fqdns.append(target.split('@')[1])
        return fqdns

    def get_server_fqdns(self):
        # make fsid real for multiple cluster; for now passing None
        serverset = set(self.get_service_fqdns(None, 'mon') +
                        self.get_service_fqdns(None, 'osd'))
        return list(serverset)

    def shutdown(self):
        log.info('Resetting CRUSH map on shutdown')
        temp_crushmap_filename = "/tmp/test_crush_map"
        self._run_command(self._get_admin_node(), "sudo ceph --cluster {c} osd setcrushmap -i {crush_name}".format(c=self.cluster_name, crush_name=temp_crushmap_filename))

    def get_fqdns(self, fsid):
        # TODO when we support multiple cluster change this
        return self.get_server_fqdns()

    def go_dark(self, fsid, dark=True, minion_id=None):
        action = 'stop' if dark else 'start'
        for target in self.get_fqdns(fsid):
            if minion_id and minion_id not in target:
                continue
            self._run_command(target, "sudo service salt-minion {action}".format(action=action))

    def reset_crush_map(self):
        """
        This depends on the map being good on first run and the admin_node being stable because it is the persistance of the tempfile that make this work
        """
        # TODO make this more robust
        temp_crushmap_filename = "/tmp/test_crush_map"
        log.info('Resetting CRUSH map')
        # get map store it
        self._run_command(self._get_admin_node(), "ls {crush_name} || sudo ceph --cluster {c} osd getcrushmap -o {crush_name}".format(c=self.cluster_name, crush_name=temp_crushmap_filename))

    def _wait_for_state(self, command, state):
        log.info('Waiting for {state} on cluster'.format(state=state))
        scalable_wait_until_true(lambda: state(command()))

    def _list_pgs(self):
        # TODO stop scraping this, defer this because pg stat -f json-pretty is anything but
        return self._run_command(self._get_admin_node(),
                                 "sudo ceph --cluster {cluster} pg stat".format(
                                     cluster=self.cluster_name))

    def _check_pgs_active_and_clean(self, output):
        total_stat, pg_stat = output.replace(';', ':').split(':')[1:3]
        return 'active+clean' == pg_stat.split()[1] and total_stat.split()[0] == pg_stat.split()[0]

    def _list_osds(self):
        return json.loads(self._run_command(self._get_admin_node(),
                                            "sudo ceph --cluster {cluster} osd dump -f json-pretty".format(
                                                cluster=self.cluster_name)))

    def _check_osds_in_and_up(self, osds):
        osd_down = [osd['osd'] for osd in osds['osds'] if not osd['up']]
        osd_out = [osd['osd'] for osd in osds['osds'] if not osd['in']]
        return not osd_down + osd_out

    def reset_all_osds(self, osd_stat):
        # this structure doesn't contain weight in dumpling = default 0
        for osd in [osd['osd'] for osd in osd_stat['osds'] if int(float(osd.get('weight', 0))) != 1]:
            self._run_command(self._get_admin_node(), 'sudo ceph osd reweight {osd_id} 1.0'.format(osd_id=osd))

        for flag in ['pause']:
            self._run_command(self._get_admin_node(), "sudo ceph --cluster ceph osd unset {flag}".format(flag=flag))

    def _list_pools(self):
        pools = json.loads(self._run_command(self._get_admin_node(),
                                             "sudo ceph --cluster {cluster} osd lspools -f json-pretty".format(
                                                 cluster=self.cluster_name)))
        return set([x['poolname'] for x in pools])

    def _check_default_pools_only(self, pools):
        return self.default_pools == pools

    def reset_all_pools(self, existing_pools):
        for pool in self.default_pools - existing_pools:
            self._run_command(self._get_admin_node(), 'sudo ceph osd pool create {pool} 64'.format(pool=pool))

        for pool in existing_pools - self.default_pools:
            self._run_command(self._get_admin_node(), 'sudo ceph osd pool delete {pool} {pool} --yes-i-really-really-mean-it'.format(
                pool=pool))

    def restart_minions(self):
        for target in self.get_fqdns(None):
            self._run_command(target, 'sudo service salt-minion restart')

    @run_once
    def _bootstrap(self, master_fqdn, distro='ubuntu'):
        for target in self.get_fqdns(None):
            log.info('Bootstrapping salt-minion on {target}'.format(target=target))

            url = 'http://{fqdn}/api/v2/info'.format(fqdn=master_fqdn)
            info = json.loads(urllib2.urlopen(url).read())

            try:
                # TODO subshell here, _run_command only halts the tests if the salt-minion restart fails
                # Also that would mean that we'd need to make apt-get update run clean
                # it currently fails due to lack of i386 packages in precise
                bootstrap_cmd = '''{bootstrap};
                    sudo sed -i 's/^[#]*open_mode:.*$/open_mode: True/;s/^[#]*log_level:.*$/log_level: debug/' /etc/salt/minion;
                    sudo service salt-minion stop
                    sudo killall salt-minion;
                    sudo service salt-minion start'''.format(bootstrap=info['bootstrap_{distro}'.format(distro=self.cluster_distro)])
            except KeyError:
                raise NotImplementedError('Cannot bootstrap a {distro} cluster'.format(distro=self.cluster_distro))

            output = self._run_command(target, bootstrap_cmd)
            log.info(output)

    def _get_admin_node(self):
        # return the first monitor we find
        return self.get_service_fqdns(None, 'mon')[0]

    def mark_osd_in(self, fsid, osd_id, osd_in=True):
        command = 'in' if osd_in else 'out'
        output = self._run_command(
            self._get_admin_node(),
            "sudo ceph --cluster {cluster} osd {command} {id}".format(
                cluster=self.cluster_name, command=command, id=int(osd_id)
            )
        )
        log.info(output)

    def restart_osd(self, fsid, fqdn, osd_id):
        output = self._run_command(
            fqdn,
            "sudo service ceph restart osd.{id}".format(id=osd_id))
        log.info(output)


if __name__ == "__main__":
    externalctl = ExternalCephControl()
    assert isinstance(externalctl.config, dict)
