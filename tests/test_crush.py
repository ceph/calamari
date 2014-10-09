import logging
import uuid

from tests.server_testcase import RequestTestCase

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

        rack_name = str(uuid.uuid1())
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket-type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": 6553,
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
                 'bucket-type': 'datacenter',
                 'items': [{'id': rack_id, 'weight': 0.1, 'pos': 0}],
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        self._wait_for_completion(r)
        # unique name assuming no collisions
        crush = {'name': rack_name,
                 'bucket-type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": 6553,
                      "pos": 0},
                     {"id": -3,
                      "weight": 6553,
                      "pos": 0}
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
                 'bucket-type': 'rack',
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
                 'bucket-type': 'rack',
                 'items': [
                     {"id": -2,
                      "weight": 6553,
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
                 'bucket-type': 'rack',
                 'items': [
                     {"id": -2000,
                      "weight": 6553,
                      "pos": 0}
                 ]
                 }
        r = self.api.post("cluster/%s/crush_node" % cluster_id, crush)
        assert r.status_code == 404

        fixed_crush = {'name': rack_name,
                       'bucket-type': 'rack',
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
