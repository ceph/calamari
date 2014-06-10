from time import sleep
from tests.server_testcase import RequestTestCase

# How long for cthulhu to mark a job as errored after losing contact?
JOB_STALE_TIMEOUT = 20 * 4  # TICK_PERIOD * 3 threshold plus one period


class TestJobExecution(RequestTestCase):
    def setUp(self):
        super(TestJobExecution, self).setUp()
        self.ceph_ctl.configure(1)
        self.calamari_ctl.configure()
        self.fsid = self._wait_for_cluster()
        self._wait_for_servers()

    def _debug_job(self, cmd, args):
        fqdn = self.api.get("server").json()[0]['fqdn']
        response = self.api.post("server/{0}/debug_job".format(fqdn), {
            'cmd': cmd,
            'args': args
        })
        self.assert_status(response, 202)
        request_id = response.json()['request_id']

        return request_id

    def test_minion_death(self):
        """
        Test that if a minion dies while jobs are executing, calamari
        server notices that the jobs have gone away and marks them failed.

        This is verifying the RequestCollection.tick logic.
        """
        request_id = self._debug_job('ceph.selftest_block', [])

        self.ceph_ctl.go_dark(self.fsid)

        self._wait_for_request(request_id, timeout=JOB_STALE_TIMEOUT, check=False)

        response = self.api.get("request/{0}".format(request_id))
        request_after_completion = response.json()
        self.assertEqual(request_after_completion['state'], "complete")
        self.assertEqual(request_after_completion['error'], True)
        self.assertEqual(request_after_completion['error_message'], "Lost contact")

    def test_minion_exception(self):
        """
        Test that if a salt minion module throws an exception, the job gets
        marked as complete.

        Use ceph.selftest_exception
        """
        request_id = self._debug_job('ceph.selftest_exception', [])

        self._wait_for_request(request_id, check=False)

        response = self.api.get("request/{0}".format(request_id))
        request_after_completion = response.json()
        self.assertEqual(request_after_completion['state'], "complete")
        self.assertEqual(request_after_completion['error'], True)
        self.assertIn("This is a self-test exception", request_after_completion['error_message'])

    def test_long_running(self):
        """
        Test that a long-running remote operation isn't killed as long
        as it remains alive

        Use ceph.selftest_wait
        """

        duration = 120

        request_id = self._debug_job('ceph.selftest_wait', [duration])

        sleep(duration / 2)

        # It should still be  running after half its duration
        request = self.api.get("request/{0}".format(request_id)).json()
        self.assertEqual(request['state'], 'submitted')

        # It should subsequently complete successfully
        self._wait_for_request(request_id, timeout=duration)

        response = self.api.get("request/{0}".format(request_id))
        request_after_completion = response.json()
        self.assertEqual(request_after_completion['state'], "complete")
        self.assertEqual(request_after_completion['error'], False)

    def test_cancellation(self):
        """
        Test that a job which never completes on its own can be killed
        by the user.

        Use ceph.selftest_block
        """
        request_id = self._debug_job('ceph.selftest_block', [])
        response = self.api.post("request/{0}/cancel".format(request_id))
        self.assert_status(response, 200)

        request_after_cancel = response.json()
        self.assertEqual(request_after_cancel['state'], "complete")
        self.assertEqual(request_after_cancel['error'], True)
        self.assertEqual(request_after_cancel['error_message'], "Cancelled")
