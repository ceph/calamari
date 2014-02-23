from copy import deepcopy
import logging
import mock
from rest_framework import status
from minion_sim.ceph_cluster import CephCluster
from tests.rest_api_unit_test import RestApiUnitTest


log = logging.getLogger(__name__)


class TestMon(RestApiUnitTest):
    SERVERS = ['server1', 'server2', 'server3']

    def assertQuorumState(self, *args):
        response = self.client.get("/api/v2/cluster/%s/mon" % self.fsid)
        self.assertStatus(response, status.HTTP_200_OK)

        expected = dict(zip(self.SERVERS, args))
        api_result = dict([(m['server'], m['in_quorum']) for m in response.data])
        self.assertDictEqual(expected, api_result)

    def setUp(self):
        super(TestMon, self).setUp()

        # I'm using CephCluster to generate the status objects to use as fixtures, I'm not
        # actually running the simulator or anything like that because this is a unit test.
        cluster = CephCluster()
        cluster.create(self.SERVERS)
        self.fsid = cluster.fsid

        # This will appear to be a completely happy healthy quorum of mons
        self.mon_status = cluster.get_cluster_object('ceph_fake', 'mon_status', None)['data']

        # XXX hmm, perhaps synthesizing this stuff should go into
        # ceph_cluster and then it be sensibly kept up to date with
        # synthesized quorum changes.
        self.server1_status = deepcopy(self.mon_status)
        self.server2_status = deepcopy(self.mon_status)
        self.server3_status = deepcopy(self.mon_status)
        for (server_status, name, rank, state) in [
            (self.server1_status, 'server1', 0, 'leader'),
            (self.server2_status, 'server2', 1, 'peon'),
            (self.server3_status, 'server3', 2, 'peon'),
        ]:
            server_status['name'] = name
            server_status['rank'] = rank
            server_status['state'] = state

        self.service_status = [
            {
                'id': 'server1',
                'type': 'mon',
                'cluster': cluster.name,
                'fsid': cluster.fsid,
                'status': self.server1_status,
                'server': 'server1',
                'running': True
            },
            {
                'id': 'server1',
                'type': 'mon',
                'cluster': cluster.name,
                'fsid': cluster.fsid,
                'status': self.server2_status,
                'server': 'server2',
                'running': True
            },
            {
                'id': 'server1',
                'type': 'mon',
                'cluster': cluster.name,
                'fsid': cluster.fsid,
                'status': self.server3_status,
                'server': 'server3',
                'running': True
            }
        ]
        self.rpc.get_sync_object = mock.Mock(return_value=self.mon_status)
        self.rpc.status_by_service = mock.Mock(return_value=self.service_status)

    def test_out_of_quorum(self):
        """That quorum-less situation is reported reasonably"""

        # Initial healthy case: everything up, everything agrees
        self.assertQuorumState(True, True, True)

        # Now let's simulate server 1 going offline.  We will stop getting
        # service updates so his local mon_status report record will continue
        # to claim he's online, but the mon cluster will notice his absence
        # so the map will assert he is offline.
        log.info("Server 1 leaves")
        self.mon_status['quorum'] = [1, 2]  # i.e. everyone but 0
        self.mon_status['election_epoch'] += 1
        self.server2_status['quorum'] = self.mon_status['quorum']
        self.server2_status['election_epoch'] = self.mon_status['election_epoch']
        self.server3_status['quorum'] = self.mon_status['quorum']
        self.server3_status['election_epoch'] = self.mon_status['election_epoch']
        self.assertQuorumState(False, True, True)

        # Now let's simulate server 2 going offline as well.  We will stop getting
        # cluster-wide mon status, the only inputs will be the local status of
        # server 3, who will tell us that he is no longer in a quorum.
        log.info("Server 2 leaves")
        self.server3_status['quorum'] = []
        self.assertQuorumState(False, False, False)

        # Server 1 comes back online
        log.info("Server 1 rejoins")
        self.mon_status['quorum'] = [0, 2]
        self.mon_status['election_epoch'] += 1
        self.server1_status['quorum'] = self.mon_status['quorum']
        self.server1_status['election_epoch'] = self.mon_status['election_epoch']
        self.server3_status['quorum'] = self.mon_status['quorum']
        self.server3_status['election_epoch'] = self.mon_status['election_epoch']
        self.assertQuorumState(True, False, True)

        # Server 2 comes back online
        log.info("Server 2 rejoins")
        self.mon_status['quorum'] = [0, 1, 2]
        self.mon_status['election_epoch'] += 1
        self.server1_status['quorum'] = self.mon_status['quorum']
        self.server1_status['election_epoch'] = self.mon_status['election_epoch']
        self.server2_status['quorum'] = self.mon_status['quorum']
        self.server2_status['election_epoch'] = self.mon_status['election_epoch']
        self.server3_status['quorum'] = self.mon_status['quorum']
        self.server3_status['election_epoch'] = self.mon_status['election_epoch']
        self.assertQuorumState(True, True, True)

    def test_service_sudden_death(self):
        """
        That when mon services are offline, a quorum is not reported.
        """
        log.info("Mon services stop")
        self.service_status[0]['running'] = False
        self.service_status[1]['running'] = False
        self.service_status[2]['running'] = False
        self.assertQuorumState(False, False, False)

    def test_server_sudden_death_majority(self):
        """
        That when a majority of servers die together, we can conclude that quorum is lost from the minority.
        """
        log.info("Servers 1 and 2 simultaneously go offline")
        self.server3_status['quorum'] = []
        self.assertQuorumState(False, False, False)
