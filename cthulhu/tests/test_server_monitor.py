

import json
import os

os.environ['CALAMARI_CONFIG'] = os.path.join(os.path.dirname(__file__), "../../dev/calamari.conf")

from django.utils.unittest.case import TestCase
from mock import Mock

from cthulhu.manager.server_monitor import ServerMonitor, ServiceId


def load_fixture(name):
    return json.load(
        open(os.path.join(os.path.dirname(__file__), name), 'r')
    )

OSD_MAP = load_fixture('osd_map.json')

# After migrating osd.1 from gravel2 to gravel1
OSD_MAP_MIGRATED = load_fixture('osd_map_migrated.json')
MON_CEPH_SERVICES_MIGRATED = load_fixture('gravel1.rockery_services_migrated.json')

# After removing osd.1
OSD_MAP_1_REMOVED = load_fixture('osd_map_1_removed.json')


FSID = "d530413f-9030-4daa-aba5-dfe3b6c4bb25"
MON_CEPH_SERVICES = load_fixture('gravel1.rockery_services.json')
MON_HOSTNAME = 'gravel1'
MON_FQDN = 'gravel1.rockery'

OSD_HOSTNAME = 'gravel2'
OSD_FQDN = 'gravel2.rockery'
OSD_CEPH_SERVICES = load_fixture('gravel2.rockery_services.json')


class TestServiceDetection(TestCase):
    """
    Exercise ServerMonitor with mock data for a two-server cluster with
    one mon and two OSDs.
    """
    def test_managed_servers(self):
        """
        That managed servers (those sending salt messages) generate
        a correct view of service locations
        """
        sm = ServerMonitor(Mock())
        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_service_heartbeat(OSD_FQDN, OSD_CEPH_SERVICES)

        self.assertEqual(len(sm.servers), 2)
        self.assertEqual(len(sm.services), 3)
        self.assertEqual(len(sm.fsid_services), 1)
        self.assertEqual(len(sm.hostname_to_server), 2)

        self.assertListEqual(sm.servers.keys(), [MON_FQDN, OSD_FQDN])
        self.assertEqual(sm.servers[OSD_FQDN].fqdn, OSD_FQDN)
        self.assertListEqual(sm.servers[MON_FQDN].services.keys(), [
            ServiceId(FSID, 'mon', MON_HOSTNAME)
        ])
        self.assertListEqual(sm.servers[OSD_FQDN].services.keys(), [
            ServiceId(FSID, 'osd', '1'),
            ServiceId(FSID, 'osd', '0')
        ])

    def test_unmanaged_servers(self):
        """
        That when only the mons are sending salt messages, we generate
        a correct view of service locations including OSDs.
        """
        sm = ServerMonitor(Mock())

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_osd_map(OSD_MAP)

        self.assertEqual(len(sm.servers), 2)
        self.assertEqual(len(sm.services), 3)
        self.assertEqual(len(sm.fsid_services), 1)
        self.assertEqual(len(sm.hostname_to_server), 2)

        self.assertListEqual(sm.servers[MON_FQDN].services.keys(), [
            ServiceId(FSID, 'mon', MON_HOSTNAME)
        ])
        self.assertListEqual(sm.servers[OSD_HOSTNAME].services.keys(), [
            ServiceId(FSID, 'osd', '1'),
            ServiceId(FSID, 'osd', '0')
        ])

    def test_unmanaged_managed_transition(self):
        """
        That when a pesky user doesn't initially install salt on OSD servers
        but later adds it, we correctly transition from paying attention
        to the CRUSH config to paying attention to the salt data, and
        fill in the correct FQDNs.
        """
        sm = ServerMonitor(Mock())

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_osd_map(OSD_MAP)

        self.assertListEqual(sm.servers.keys(), [MON_FQDN, OSD_HOSTNAME])
        self.assertListEqual(sm.servers[MON_FQDN].services.keys(), [
            ServiceId(FSID, 'mon', MON_HOSTNAME)
        ])
        self.assertListEqual(sm.servers[OSD_HOSTNAME].services.keys(), [
            ServiceId(FSID, 'osd', '1'),
            ServiceId(FSID, 'osd', '0')
        ])

        sm.on_service_heartbeat(OSD_FQDN, OSD_CEPH_SERVICES)

        self.assertListEqual(sm.servers.keys(), [MON_FQDN, OSD_FQDN])
        self.assertEqual(sm.servers[OSD_FQDN].fqdn, OSD_FQDN)
        self.assertListEqual(sm.servers[MON_FQDN].services.keys(), [
            ServiceId(FSID, 'mon', MON_HOSTNAME)
        ])
        self.assertListEqual(sm.servers[OSD_FQDN].services.keys(), [
            ServiceId(FSID, 'osd', '1'),
            ServiceId(FSID, 'osd', '0')
        ])

    def test_unmanaged_service_relocate(self):
        """
        That when an OSD disappears from one server's salt.services output
        and reappears on another server, this is reflected in the state.
        """
        sm = ServerMonitor(Mock())

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_osd_map(OSD_MAP)

        # osd.1 initially on unmanaged server OSD
        self.assertEqual(sm.services[ServiceId(FSID, 'osd', "1")].server_state.fqdn, OSD_HOSTNAME)

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES_MIGRATED)
        sm.on_osd_map(OSD_MAP_MIGRATED)

        # osd.1 now on managed server MON
        self.assertEqual(sm.services[ServiceId(FSID, 'osd', "1")].server_state.fqdn, MON_FQDN)

        # Check the servers' lists of services are up to date too
        self.assertListEqual(sm.servers[MON_FQDN].services.keys(), [
            ServiceId(FSID, 'osd', '1'),
            ServiceId(FSID, 'mon', MON_HOSTNAME)

        ])
        self.assertListEqual(sm.servers[OSD_HOSTNAME].services.keys(), [
            ServiceId(FSID, 'osd', '0')
        ])

    def test_remove_managed(self):
        """
        That when a managed server is removed, it no longer appears
        in the server/service data.
        """
        sm = ServerMonitor(Mock())

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_service_heartbeat(OSD_FQDN, OSD_CEPH_SERVICES)

        sm.remove(OSD_FQDN)

        # The two OSD services, and the 'osd' server should be gone
        self.assertEqual(len(sm.servers), 1)
        self.assertEqual(len(sm.services), 1)
        self.assertEqual(len(sm.fsid_services), 1)
        self.assertEqual(len(sm.hostname_to_server), 1)

        self.assertListEqual(sm.servers.keys(), [MON_FQDN])
        self.assertListEqual(sm.services.keys(), [ServiceId(FSID, 'mon', MON_HOSTNAME)])
        self.assertListEqual([s.id for s in sm.fsid_services[FSID]], [ServiceId(FSID, 'mon', MON_HOSTNAME)])
        self.assertListEqual(sm.hostname_to_server.keys(), [MON_HOSTNAME])

    def test_remove_server(self):
        """
        That when an OSD is disappears from the OSD map, it is also removed
        from ServerMonitor's worldview
        """
        sm = ServerMonitor(Mock())

        sm.on_service_heartbeat(MON_FQDN, MON_CEPH_SERVICES)
        sm.on_service_heartbeat(OSD_FQDN, OSD_CEPH_SERVICES)

        self.assertEqual(len(sm.servers), 2)
        self.assertEqual(len(sm.services), 3)
        self.assertEqual(len(sm.fsid_services), 1)
        self.assertEqual(len(sm.hostname_to_server), 2)

        sm.on_osd_map(OSD_MAP_1_REMOVED)

        self.assertEqual(len(sm.servers), 2)
        self.assertEqual(len(sm.services), 2)  # decremented by 1
        self.assertEqual(len(sm.fsid_services), 1)
        self.assertEqual(len(sm.hostname_to_server), 2)
