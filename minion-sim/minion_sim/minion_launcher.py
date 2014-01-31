import errno
import getpass
import os
import signal
import subprocess
import threading
import xmlrpclib
from diamond.metric import Metric
from jinja2 import Template
from diamond.handler.graphite import GraphiteHandler
from minion_sim.log import log


STATS_PERIOD = 10

MINION_CONFIG_TEMPLATE = """
master: localhost
id: {{ FQDN }}
user: {{ USER }}
pidfile: {{ ROOT }}/var/run/salt-minion.pid
pki_dir: {{ ROOT }}/etc/pki
cachedir: {{ ROOT }}/var/cache
log_file: {{ ROOT }}/var/log/salt/minion
sock_dir: /tmp
grains:
    fqdn: {{ FQDN}}
    localhost: {{ HOSTNAME }}
    host: {{ HOSTNAME }}
    nodename: {{ HOSTNAME }}
"""


class LongMarshaller(xmlrpclib.Marshaller):
    """
    Break XMLRPC standard to send >32bit integers

    The (correct) default implementation raises OverflowError
    when we send a value bigger than 4 gigs.
    """
    dispatch = xmlrpclib.Marshaller.dispatch

    def dump_int(self, value, write):
        write("<value><int>")
        write(str(value))
        write("</int></value>\n")
    dispatch[xmlrpclib.IntType] = dump_int

xmlrpclib.Marshaller = LongMarshaller
xmlrpclib.FastMarshaller = None


class StatsSender(threading.Thread):
    """
    A baby version of diamond+CephCollector, sending
    fictional statistics to graphite.
    """
    def __init__(self, fqdn, cluster):
        super(StatsSender, self).__init__()
        self._handler = GraphiteHandler({
            'host': 'localhost'
        })
        self._complete = threading.Event()
        self._fqdn = fqdn
        self._cluster = cluster

    def run(self):
        while not self._complete.is_set():
            self._get_stats()
            self._complete.wait(STATS_PERIOD)

    def stop(self):
        self._complete.set()

    def _get_stats(self):
        """
        Synthesize statistics and submit them to
        the graphite handler
        """

        for metric, value in self._cluster.get_stats(self._fqdn):
            self._handler.process(
                Metric(metric, value)
            )


class MinionLauncher(object):
    """
    Wrapper for a child/subprocess.

    Responsible for creating the filesystem tree for this salt
    minion, writing out a config file and then starting/stopping it.
    """
    def __init__(self, rpc_url, config_dir, hostname, fqdn, cluster=None):
        super(MinionLauncher, self).__init__()

        self.ps = None
        self.hostname = hostname
        self.fqdn = fqdn

        path = os.path.join(config_dir, self.hostname)

        try:
            os.makedirs(path)
            os.makedirs(os.path.join(path, 'var/run'))
            os.makedirs(os.path.join(path, 'etc/salt'))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        config_str = Template(MINION_CONFIG_TEMPLATE).render(
            HOSTNAME=self.hostname,
            USER=getpass.getuser(),
            ROOT=path,
            FQDN=self.fqdn
        )

        config_filename = os.path.join(path, 'etc/salt/minion')
        open(config_filename, 'w').write(config_str)

        self._rpc_url = rpc_url

        self.cmdline = ['-c', os.path.dirname(config_filename)]
        self._stats_sender = None

        # Cluster may be in or out of process
        if cluster is None:
            self._cluster = xmlrpclib.ServerProxy(rpc_url, allow_none=True)
        else:
            self._cluster = cluster

    def start(self):
        # TODO: send stdout and stderr somewhere other than the screen to avoid spamming
        # during test runs

        env = os.environ.copy()
        env['RPC_URL'] = self._rpc_url
        self.ps = subprocess.Popen(['minion-child'] + self.cmdline,
                                   stdin=subprocess.PIPE, env=env)
        self._stats_sender = StatsSender(self.fqdn, self._cluster)
        self._stats_sender.start()

    def stop(self):
        try:
            log.info("Sending SIGTERM to %s" % self.ps.pid)
            self.ps.send_signal(signal.SIGTERM)
        except OSError as e:
            if e.errno == errno.ESRCH:
                print "Process not found, killing minion %s" % self.ps.pid
                # Process not found, i.e. it's already dead.
                pass
            else:
                raise

        self._stats_sender.stop()

    def join(self):
        log.info("Waiting for %s (%s)" % (self.ps.pid, self.fqdn))
        self.ps.communicate()
        log.info("Process %s completed" % self.ps.pid)
        self._stats_sender.join()
        log.info("Stats sender[%s] complete" % self.fqdn)
