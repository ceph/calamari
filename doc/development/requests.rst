
How requests are executed
=========================

1. Constructing a UserRequest object
------------------------------------

Requests are initiated by a REST API consumer (our web interface, or
some third party software), using a POST (create), PATCH (modify) or DELETE
verb.  We also use this interface from integration tests, for example TestPoolManagement.

The relevant ``ViewSet`` subclass is responsible for implementing the verbs, and
translating the HTTP request into an RPC to cthulhu.  For example, PoolViewSet.update
invokes the ``update`` RPC with arguments indicating the type of object (types.POOL),
the FSID of the cluster, and the pool ID.  The RPC returns a request ID, which
is returned in the HTTP response, with the status set to 202 (accepted).

The RPC to cthulhu is handled in RpcInterface, which typically resolves a FSID to
a ClusterMonitor instance and calls through to the appropriate method on that
ClusterMonitor.  For example, RpcInterface.update calls through to
ClusterMonitor.request_update.

ClusterMonitor handles requests by resolving the object type (for example POOL)
to a RequestFactory subclass in ClusterMonitor.request.  For example, our
update to a pool is handled by a PoolRequestFactory instance.  Request factories
are responsible for mapping a create, update or delete operation into an instance
of a UserRequest subclass, with some remote commands to run.

For example, and update request for a pool called 'foopool' might look like this
when passed into PoolRequestFactory.update:

::
    pool_id=7
    attributes={
        'quota_max_bytes': 1024000000,
        'quota_max_objects': 1000000
    }

This is used to construct an OsdMapModifyingRequest with a list of ceph commands
like this:

::
    commands=[
        ('osd pool set-quota', {'pool': 'foopool', 'field': 'max_bytes', 'val': 1024000000}),
        ('osd pool set-quota', {'pool': 'foopool', 'field': 'max_objects', 'val': 1000000}),
    ]

The OsdMapModifyingRequest is a type of UserRequest which runs some ceph commands, reads
the resulting OSD map epoch after the commands, and then waits for the OSD map with
that epoch to arrive at the Calamari server.

2. Running a UserRequest object
-------------------------------

Once the request object has been constructed, it is ready to be executed.

TODO: write this once i've rearranged things so that request updates
go through requestcollection so that things that create >1 JID can
keep the map of JID->request up to date.
