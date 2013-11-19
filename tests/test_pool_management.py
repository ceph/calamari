from django.utils.unittest.case import skipIf
from tests.server_testcase import ServerTestCase


class TestPoolManagement(ServerTestCase):
    @skipIf(True, "not implemented yet")
    def test_create(self):
        """
        Test that a well formed pool creation request is accepted and actioned.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_add_pgs(self):
        """
        Test that a well formed request to raise the number of PGs in a pool is
        accepted and actioned.
        """
        pass