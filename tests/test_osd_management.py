import logging
from tests.server_testcase import RequestTestCase


log = logging.getLogger(__name__)


class TestOsdManagement(RequestTestCase):
    def setUp(self):
        super(TestOsdManagement, self).setUp()
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()

    def test_update(self):
        """
        That valid updates succeed and take effect
        """
        updates = {
            'in': False,
            'up': False,
            'reweight': 0.5
        }

        osd_id = 0
        fsid = self._wait_for_cluster()

        for k, v in updates.items():
            log.debug("Updating %s=%s" % (k, v))
            osd_url = "cluster/%s/osd/%s" % (fsid, osd_id)

            # Check that the modification really is a modification and
            # not the status quo
            osd = self.api.get(osd_url).json()
            self.assertNotEqual(osd[k], v)

            # Apply the modification
            response = self.api.patch(osd_url, {k: v})
            self._wait_for_completion(response)

            # After completion the update should be visible
            # NB this is slightly racy on a real cluster because when we mark something
            # down it will at some point get marked up again, hopefully not so quickly
            # that we fail this check.  But if this is mysteriously failing, yeah.  That.

            osd = self.api.get(osd_url).json()
            self.assertEqual(osd[k], v)

    def test_no_op_updates(self):
        """
        That no-op updates get a 304 response
        """
        no_op_updates = {
            'in': True,
            'up': True,
            'reweight': 1.0
        }

        osd_id = 0
        fsid = self._wait_for_cluster()

        for k, v in no_op_updates.items():
            osd_url = "cluster/%s/osd/%s" % (fsid, osd_id)
            osd = self.api.get(osd_url).json()
            self.assertEqual(osd[k], v)
            response = self.api.patch(osd_url, {k: v})
            self.assertEqual(response.status_code, 304)
            osd = self.api.get(osd_url).json()
            self.assertEqual(osd[k], v)

    def test_apply(self):
        """
        That we can apply ceph commands to an OSD
        """
        commands = ['scrub', 'deep_scrub', 'repair']
        osd_id = 0
        fsid = self._wait_for_cluster()

        osd_url = "cluster/%s/osd/%s" % (fsid, osd_id)
        osd = self.api.get(osd_url).json()
        self.assertEqual(osd['up'], True)

        osd_url = "cluster/%s/osd/%s/command" % (fsid, osd_id)
        response = self.api.get(osd_url)
        self.assertEqual(response.status_code, 200, 'HTTP status not 200 for %s' % osd_url)
        osd = response.json()

        for x in commands:
            self.assertIn(x, osd.get(str(osd_id)).get('valid_commands'))
            osd_url = "cluster/%s/osd/%s/command/%s" % (fsid, osd_id, x)
            response = self.api.post(osd_url)
            self.assertEqual(response.status_code, 202, 'HTTP status not 202 for %s' % osd_url)

    def test_osd_config_change(self):
        """
        That we can change the flags on an OsdMap
        """
        fsid = self._wait_for_cluster()

        url = "cluster/%s/osd_config" % (fsid)

        config = self.api.get(url).json()

        self.assertEqual(False, config['pause'])

        response = self.api.patch(url, data={"pause": True})
        self._wait_for_completion(response)

        config = self.api.get(url).json()
        self.assertEqual(True, config['pause'])
