from SimpleXMLRPCServer import SimpleXMLRPCServer
import argparse
import os
import threading
from minion_sim.ceph_cluster import CephCluster
from minion_sim.constants import XMLRPC_PORT
from minion_sim.load_gen import LoadGenerator
from minion_sim.minion_launcher import MinionLauncher


PREFIX = 'figment'
DOMAIN = 'imagination.com'


def get_dns(index):
    hostname = "{0}{1:03d}".format(PREFIX, index)
    fqdn = "{0}.{1}".format(hostname, DOMAIN)

    return hostname, fqdn


class MinionSim(threading.Thread):
    def __init__(self, config_dir, count):
        super(MinionSim, self).__init__()
        self._config_dir = config_dir
        self._count = count
        self._server = None
        self._server_available = threading.Event()
        self.minions = []

    def get_minion_fqdns(self):
        return [m.fqdn for m in self.minions]

    def start(self):
        super(MinionSim, self).start()
        self._server_available.wait()

    def run(self):
        config_file = os.path.join(self._config_dir, 'cluster.json')
        if not os.path.exists(config_file):
            CephCluster.create(config_file, [get_dns(i)[1] for i in range(0, self._count)])
        cluster = CephCluster(config_file)

        # Start an XMLRPC service for the minions' fake ceph plugins to
        # get their state
        self._server = SimpleXMLRPCServer(("localhost", XMLRPC_PORT), allow_none=True)
        self._server.register_instance(cluster)

        for i in range(0, self._count):
            hostname, fqdn = get_dns(i)
            self.minions.append(MinionLauncher(self._config_dir, hostname, fqdn, cluster))

        # Quick smoke test that these methods aren't going
        # to throw exceptions (rather stop now than get exceptions
        # remotely)
        for minion in self.minions:
            cluster.get_stats(minion.fqdn)

        # A thread to generate some synthetic activity on the synthetic cluster
        load_gen = LoadGenerator(cluster)
        load_gen.start()

        for minion in self.minions:
            minion.start()

        self._server_available.set()
        self._server.serve_forever()

        load_gen.stop()
        for minion in self.minions:
            minion.stop()
        load_gen.join()
        for minion in self.minions:
            minion.join()

        cluster.save()

    def stop(self):
        self._server.shutdown()


def main():
    parser = argparse.ArgumentParser(description='Start simulated salt minions.')
    parser.add_argument('--count', dest='count', type=int, default=3, help='Number of simulated minions')
    args = parser.parse_args()

    config_path = os.getcwd()

    sim = MinionSim(config_path, args.count)

    sim.start()
    try:
        sim.join()
    except KeyboardInterrupt:
        sim.stop()
        sim.join()
        pass