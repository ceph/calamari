

class Unavailable(Exception):
    pass


class Remote(object):
    """
    The interface for cthulhu to talk to the outside world.
    """

    def run_job_sync(self, fqdn, cmd, args):
        """
        Run one python function from our remote module, and wait
        for a response or raise Unavailable
        """
        raise NotImplementedError()

    def run_job(self, fqdn, cmd, args):
        """
        Start running a python function from our remote module,
        and return the job ID
        """
        raise NotImplementedError()

    def get_local_metadata(self):
        """
        Return the metadata for this host that we are running
        on.
        """
        raise NotImplementedError()

    def get_remote_metadata(self, fqdns):
        """
        Return a dict of FQDN to grain dictionary for remote servers.

        Any servers for which metadata is not found will appear in the result
        with an empty dictionary
        """
        raise NotImplementedError()

    def get_heartbeat_period(self, fqdn):
        """
        Return the period in seconds between heartbeats
        """
        raise NotImplementedError()

    def get_running(self, fqdns):
        """
        Send a request to discover which job IDs are running on
        the specified hosts.  Wait for the response with listen()
        """
        raise NotImplementedError()

    def cancel(self, fqdn, jid):
        """
        Send a request to cancel a job on a particular host.  There
        is no feedback about whether the cancellation really happened.
        """
        raise NotImplementedError()

    def auth_get(self, fqdn):
        """
        Get the authentication status of a host
        """
        raise NotImplementedError()

    def auth_list(self, status_filter):
        """
        Get the authentication status of all hosts whose statuses
        match `status_filter`.

        :param status_filter: An authentication state string, or None for no filter.
        """
        raise NotImplementedError()

    def auth_accept(self, fqdn):
        """
        Set authentication state for this host to AUTH_ACCEPTED
        """
        raise NotImplementedError()

    def auth_reject(self, fqdn):
        """
        Set authentication state for this host to AUTH_REJECTED
        """
        raise NotImplementedError()

    def auth_delete(self, fqdn):
        """
        Clear authentication state for this host
        """
        raise NotImplementedError()

    def listen(self, completion,
               on_heartbeat=None,
               on_job=None,
               on_server_heartbeat=None,
               on_running_jobs=None,
               fsid=None):
        """
        Subscribe to messages

        :param on_heartbeat: Callback for heartbeats
        :param on_job: Callback for job completions
        :param fsid: Optionally filter heartbeats to one FSID
        """
        raise NotImplementedError()


# This code was originally salt-only, so we use the salt magic values for
# authentication states of remote servers
AUTH_NEW = 'pre'
AUTH_REJECTED = 'rejected'
AUTH_ACCEPTED = 'accepted'
