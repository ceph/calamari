from django.utils.unittest import TestCase
from mock import Mock, patch


class CalamariConfig(type):
    def __new__(mcs, name, parents, dct):
        import os
        if os.environ.get("CALAMARI_CONFIG") is None:
            os.environ["CALAMARI_CONFIG"] = "/home/vagrant/calamari/dev/calamari.conf"

        return super(CalamariConfig, mcs).__new__(mcs, name, parents, dct)


class CalamariTestCase(TestCase):
    __metaclass__ = CalamariConfig

from cthulhu.manager.osd_request_factory import OsdRequestFactory
from cthulhu.manager.user_request import UserRequest


class TestOSDFactory(CalamariTestCase):

    salt_local_client = Mock(run_job=Mock())
    salt_local_client.return_value = salt_local_client
    salt_local_client.run_job.return_value = {'jid': 12345}

    def setUp(self):
        self.fake_cluster_monitor = Mock(fsid=12345)

    def testCreate(self):
        self.assertNotEqual(OsdRequestFactory(0), None, 'Test creating an OSDRequest')

    @patch('cthulhu.manager.user_request.LocalClient', salt_local_client)
    def testScrub(self):
        scrub = OsdRequestFactory(self.fake_cluster_monitor).scrub(0)
        self.assertIsInstance(scrub, UserRequest, 'Testing Scrub')

        #import pdb; pdb.set_trace()
        scrub.submit(54321)
        assert(self.salt_local_client.run_job.assert_called_with())

    def testDeepScrub(self):
        deep_scrub = OsdRequestFactory(self.fake_cluster_monitor).deep_scrub(0)
        self.assertIsInstance(deep_scrub, UserRequest, 'Failed to make a deep scrub request')

    @patch('cthulhu.manager.user_request.LocalClient', salt_local_client)
    def testUpdate(self):
        update = OsdRequestFactory(self.fake_cluster_monitor).update(0, {'id': 'fake', 'in': 1})
        update.submit(54321)
        self.salt_local_client.run_job.assert_called_with()