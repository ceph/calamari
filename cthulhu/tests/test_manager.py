from django.utils.unittest import TestCase
from django.utils.unittest.case import skipIf

import os

if os.environ.get('CALAMARI_CONFIG'):
    from cthulhu.manager import manager, rpc, derived, cluster_monitor, plugin_monitor


class TestManager(TestCase):
    def setUp(self):
        self.manager = manager.Manager()

    def tearDown(self):
        self.manager.stop()

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreateManager(self):
        assert self.manager is not None


class TestRpcThread(TestCase):
    def setUp(self):
        self.rpc_thread = rpc.RpcThread(manager.Manager())

    def tearDown(self):
        self.rpc_thread.stop()

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreateRpcThread(self):
        assert self.rpc_thread is not None


class TestDerivedObjects(TestCase):
    def setUp(self):
        self.derived_TestCase = derived.DerivedObjects()

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testDerivedObject(self):
        pass


class TestSyncObjects(TestCase):
    def setUp(self):
        self.sync_TestCases = cluster_monitor.SyncObjects('ceph')

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreateSyncObjects(self):
        pass


class TestClusterMonitor(TestCase):
    def setUp(self):
        self.cluster_monitor = cluster_monitor.ClusterMonitor(1, "None", None, None, None, None, None)

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreateClusterMonitor(self):
        pass


class TestPluginMonitor(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(None)

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreatePluginMonitor(self):
        pass
