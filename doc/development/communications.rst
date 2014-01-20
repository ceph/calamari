
Communication between Ceph servers and Calamari server
======================================================

This page is about the messages/events we send via salt, from the salt minions
running on Ceph servers to the salt master running on the Calamari server.  Cthulhu
listens to these events.  This isn't a syntax specification, it isn't that formal.

The TLDR is:

- All Ceph servers send a periodic heartbeat describing which Ceph services
  are running, and other properties of the server like the Ceph version installed.
  This is the ``ceph/server/<fqdn>`` event tag.
- Servers running the mon service send a periodic heartbeat describing the Ceph
  cluster, primarily giving a vector of versions for the cluster maps.  This is
  the ``ceph/cluster/<fsid>`` event tag.
- When Cthulhu sees mention of a cluster map version more recent than the
  one it has in hand, it executes a job on one of the mons to retrieve
  the full copy of that version of the cluster map.  This is the ``ceph.get_cluster_object``
  function.
- When Cthulhu is executing a :doc:`user request <requests`, it uses
  the ``ceph.rados_commands`` function to execute some librados operations.

All this is happening inside the communications channel that salt establishes for us.


