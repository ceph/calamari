from cthulhu.manager import manager, rpc, derived, cluster_monitor
from unittest import TestCase

class TestManager(TestCase):
    def setUp(self):
        self.manager = manager.Manager()
    
    def tearDown(self):

        self.manager.stop()

    def testCreateManager(self):
        assert self.manager != None

class TestRpcThread(TestCase):
    def setUp(self):
        self.rpc_thread = rpc.RpcThread(manager.Manager())

    def tearDown(self):
        self.rpc_thread.stop()

    def testCreateRpcThread(self):
        assert self.rpc_thread != None


class TestDerivedObjects(TestCase):

    def setUp(self):
        self.derived_TestCase = derived.DerivedObjects()

    def tearDown(self):
        pass

    def testDerivedObject(self):
        pass


class TestSyncObjects(TestCase):

    def setUp(self):
        self.sync_TestCases = cluster_monitor.SyncObjects()

    def tearDown(self):
        pass

    def testCreateSyncObjects(self):
        pass


class TestClusterMonitor(TestCase):
    def setUp(self):
        self.cluster_monitor = cluster_monitor.ClusterMonitor(1, "None", None, None, [])

    def tearDown(self):
        pass

    def testCreateClusterMonitor(self):

        pass