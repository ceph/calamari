from tests.server_testcase import ServerTestCase
from mock import MagicMock
import os
import logging


log = logging.getLogger('tests.test_permissions')

os.environ.setdefault("CALAMARI_CONFIG", "dev/calamari.conf")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")


class TestPermissions(ServerTestCase):
    def setUp(self):
        # TODO could we subclass django test case and get this for free?
        self.change_role('admin', 'superuser')
        super(TestPermissions, self).setUp()

    def tearDown(self):
        self.change_role('admin', 'superuser')
        super(TestPermissions, self).tearDown()

    def change_role(self, user, role):
        from cthulhu.calamari_ctl import assign_role
        args = MagicMock()
        args.username = user
        args.role_name = role
        assign_role(args)
        log.debug('changing role of %s to %s' % (user, role))

    def test_that_accept_header_reflects_role(self):
        """
        Check that we restrict readonly role from delete, put, patch, post
        and that we allow other roles to do so
        """

        # Spin up a running Calamari+Ceph environment
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()

        fsid = self._wait_for_cluster()
        # Unlike most tests we really do need all the servers to be there in case
        # the one we're checking for isn't.
        self._wait_for_servers()

        for url in ("cluster/{0}/osd/0",
                    "cluster/{0}/pool/0",
                    "cluster/{0}/osd_config"):
            response = self.api.get(url.format(fsid))
            response.raise_for_status()

            self.assertEqual(response.status_code, 200)
            self.assertIn('PATCH', response.headers.get('allow'))

        self.change_role('admin', 'readonly')

        # TODO expand this to cover all endpoints
        for url in ("cluster/{0}/osd/0",
                    "cluster/{0}/osd",
                    "cluster/{0}/pool/0",
                    "cluster/{0}/pool",
                    "cluster/{0}/osd_config"):
            response = self.api.get(url.format(fsid))
            response.raise_for_status()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get('allow'), 'GET, HEAD, OPTIONS')
