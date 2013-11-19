from django.utils.unittest.case import skipIf
from tests.server_testcase import ServerTestCase


class TestJobExecution(ServerTestCase):
    @skipIf(True, "not implemented yet")
    def test_master_restart(self):
        """
        Test that if calamari restarts while jobs are executing on minions,
        the new calamari instance cleans up the old jobs.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_minion_restart(self):
        """
        Test that if a minion restarts while jobs are executing, calamari
        server notices that the jobs have gone away and marks them failed.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_minion_unavailable(self):
        """
        Test that if a job is initated while its target minion is unavailable,
        we get a clean immediate failure.
        """
        pass
