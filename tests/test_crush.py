import logging
import uuid

from tests.server_testcase import RequestTestCase
from django.utils.unittest.case import skipIf

log = logging.getLogger(__name__)


class TestCrushNodeManagement(RequestTestCase):
    def setUp(self):
        super(TestCrushNodeManagement, self).setUp()
        self.ceph_ctl.configure(2)
        self.calamari_ctl.configure()

    def test_lifecycle(self):
        """
        Test that we can:
         - Create a crush node
         - Add some children to it
         - update it's name, type, and children
        """

        cluster_id = self._wait_for_cluster()

        r = self.api.get("cluster/%s/crush_node" % cluster_id).json()

        real_weights = {}
        rack_id = None
        for node in r:
            if node['id'] in (-2, -3):
                real_weights[node['id']] = node['weight']

        rack_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket_type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": real_weights[-2],
                      "pos": 0}
                 ]
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)

        r = self.api.get("cluster/%s/crush_node" % cluster_id).json()

        rack_id = None
        for node in r:
            if node['name'] == rack_name:
                rack_id = node['id']

        # unique name assuming no collisions
        crush = {'name': str(uuid.uuid1()),
                 'bucket_type': 'datacenter',
                 'items': [{'id': rack_id, 'weight': 0.1, 'pos': 0}],
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket_type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": real_weights[-2],
                      "pos": 0},
                 ]
                 }
        r = self.api.patch("cluster/{fsid}/crush_node/{node_id}".format(fsid=cluster_id, node_id=rack_id), crush)
        self._wait_for_completion(r)

        # TODO assert that the shape of the tree is right

    def test_delete_bucket(self):
        cluster_id = self._wait_for_cluster()

        rack_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket_type': 'rack',
                 'items': []
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)

        r = self.api.get("cluster/%s/crush_node" % cluster_id).json()

        rack_id = None
        for node in r:
            if node['name'] == rack_name:
                rack_id = node['id']
        r = self.api.delete("cluster/{fsid}/crush_node/{node_id}".format(fsid=cluster_id, node_id=rack_id))
        self._wait_for_completion(r)

    def test_delete_full_bucket_fails(self):
        cluster_id = self._wait_for_cluster()

        rack_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket_type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": 0.0999908447265625,
                      "pos": 0}
                 ]
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)

        r = self.api.get("cluster/%s/crush_node" % cluster_id).json()

        rack_id = None
        for node in r:
            if node['name'] == rack_name:
                rack_id = node['id']
        r = self.api.delete("cluster/{fsid}/crush_node/{node_id}".format(fsid=cluster_id, node_id=rack_id))
        assert r.status_code == 409

    def test_adding_non_existing_children_fails(self):
        cluster_id = self._wait_for_cluster()

        rack_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket_type': 'rack',
                 'items': [
                     {"id": -2000,
                      "weight": 0.0999908447265625,
                      "pos": 0}
                 ]
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        assert r.status_code == 404

        fixed_crush = {'name': rack_name,
                       'bucket_type': 'rack',
                       'items': []
                       }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, fixed_crush)
        self._wait_for_completion(r)

        r = self.api.get("cluster/%s/crush_node" % cluster_id).json()

        rack_id = None
        for node in r:
            if node['name'] == rack_name:
                rack_id = node['id']
        r = self.api.patch("cluster/{fsid}/crush_node/{node_id}".format(fsid=cluster_id, node_id=rack_id), crush)
        assert r.status_code == 404

    @skipIf(True, "needs http://tracker.ceph.com/issues/10844 or admin.keyring on all nodes")
    def test_reparented_osds_survive_osd_restart(self):
        cluster_id = self._wait_for_cluster()

        host_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': host_name,
                 'bucket_type': 'host',
                 'items': [
                     {"id": 1,
                      "weight": 0.0999908447265625,
                      "pos": 0}
                 ]
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)
        crush_nodes_before = self.api.get('cluster/%s/crush_node' % cluster_id).json()
        log.error('Crush nodes before restart ' + str(crush_nodes_before))

        for server in self.api.get("cluster/%s/server" % cluster_id).json():
            for service in server['services']:
                if service['type'] == 'osd' and service['running'] == 'true':
                    self.ceph_ctl.restart_osd(cluster_id, server['fqdn'], service['id'])
                    break

        # real clusters won't likely clean up pgs in our wait-timeout interval
        # or we'd just ask for ceph_ctl.configure here
        # TODO perhaps we should explicitly wait for the next OsdMap version
        self.ceph_ctl.wait_till_osds_up_and_in()

        crush_nodes_after = self.api.get('cluster/%s/crush_node' % cluster_id).json()
        log.error('Crush nodes after restart ' + str(crush_nodes_after))

        self.assertEqual(crush_nodes_before, crush_nodes_after)
