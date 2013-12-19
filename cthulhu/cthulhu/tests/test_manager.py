from cthulhu.manager import manager, rpc, derived, cluster_monitor


from nose.tools import with_setup


class TestManager(object):
    def setUp(self):
        self.manager = manager.Manager()
    
    def tearDown(self):

        self.manager.stop()

    def testCreateManager(self):
        assert self.manager != None

class TestRpcThread(object):
    def setUp(self):
        self.rpc_thread = rpc.RpcThread(manager.Manager())

    def tearDown(self):
        self.rpc_thread.stop()

    def testCreateRpcThread(self):
        assert self.rpc_thread != None


class TestDerivedObjects(object):

    def setUp(self):
        self.derived_object = derived.DerivedObjects()

    def tearDown(self):
        pass

    def testDerivedObject(self):
        pass


class TestSyncObjects(object):

    def setUp(self):
        self.sync_objects = cluster_monitor.SyncObjects()

    def tearDown(self):
        pass

    def testCreateSyncObjects(self):
        pass


class TestClusterMonitor(object):
    def setUp(self):
        self.cluster_monitor = cluster_monitor.ClusterMonitor(1, "None", None, None)

    def tearDown(self):
        pass

    def testCreateClusterMonitor(self):

        pass