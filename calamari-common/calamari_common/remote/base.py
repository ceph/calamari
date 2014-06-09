

class Unavailable(Exception):
    pass


class Remote(object):
    """
    The interface for cthulhu to talk to the outside world.
    """

    def run_job_sync(self, fqdn, cmd, args):
        """
        Run one python function from our remote module
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

    # Run a ceph.rados_commands

    # Get a sync_object

    # Run a logtail.*

    # List running JIDs on a list of minions
    def get_running(self, minions):
        """
        :param minion: List of minion IDs
        """
        raise NotImplementedError()

    # Cancel a JID

    # Subscribe to ceph cluster heartbeats for one cluster

    # Subscribe to ceph cluster heartbeats for all clusters

    # Subscribe to ceph server heartbeats


    # Add a minion or minion range

    # List minions with their authentication state

    # Modify a minion's authentication state

    # Get the metadata for a server

    # Get the metadata for this server (where calamari-server is running)


# This code was originally salt-only, so we use the salt magic values for
# authentication states of remote servers
AUTH_NEW = 'pre'
AUTH_REJECTED = 'rejected'
AUTH_ACCEPTED = 'accepted'
