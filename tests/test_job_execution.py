from django.utils.unittest.case import skipIf
from tests.server_testcase import ServerTestCase


class TestJobExecution(ServerTestCase):
    @skipIf(True, "not implemented yet")
    def test_minion_restart(self):
        """
        Test that if a minion restarts while jobs are executing, calamari
        server notices that the jobs have gone away and marks them failed.

        This is verifying the RequestCollection.tick logic.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_minion_unavailable(self):
        """
        Test that if a job is initated while its target minion is unavailable,
        we get a clean immediate failure.
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_minion_exception(self):
        """
        Test that if a salt minion module throws an exception, the job gets
        marked as complete.

        Use ceph.selftest_exception
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_long_running(self):
        """
        Test that a long-running remote operation isn't killed as long
        as it remains alive

        Use ceph.selftest_wait
        """
        pass

    @skipIf(True, "not implemented yet")
    def test_cancellation(self):
        """
        Test that a job which never completes on its own can be killed
        by the user.

        Use ceph.selftest_block
        """
        pass
