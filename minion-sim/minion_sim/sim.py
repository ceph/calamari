from SimpleXMLRPCServer import SimpleXMLRPCServer
import argparse
import os
from minion_sim.ceph_cluster import CephCluster
from minion_sim.constants import XMLRPC_PORT
from minion_sim.load_gen import LoadGenerator
from minion_sim.minion_launcher import MinionLauncher


def main():
    parser = argparse.ArgumentParser(description='Start simulated salt minions.')
    parser.add_argument('--count', dest='count', type=int, default=3, help='Number of simulated minions')
    args = parser.parse_args()

    minions = []
    for i in range(0, args.count):
        minions.append(MinionLauncher(i))

    if not os.path.exists('cluster.json'):
        CephCluster.create('cluster.json', [m.fqdn for m in minions])
    cluster = CephCluster('cluster.json')

    # A thread to generate some synthetic activity on the synthetic cluster
    load_gen = LoadGenerator(cluster)

    # Start an XMLRPC service for the minions' fake ceph plugins to
    # get their state
    server = SimpleXMLRPCServer(("localhost", XMLRPC_PORT), allow_none=True)
    server.register_instance(cluster)

    load_gen.start()

    for minion in minions:
        minion.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        load_gen.stop()
        for minion in minions:
            minion.stop()
        load_gen.join()
        for minion in minions:
            minion.join()

        cluster.save()