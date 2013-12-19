from cthulhu.persistence import sync_objects
from nose.tools import with_setup


class TestPersistence(object):
    def setUp(self):
        self.persister = sync_objects.Persister()
    
    def tearDown(self):

        self.persister.stop()

    def testCreateManager(self):
        assert self.persister != None