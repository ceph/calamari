
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

CRUD-type operations
~~~~~~~~~~~~~~~~~~~~

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

Command-type operations
~~~~~~~~~~~~~~~~~~~~~~~

For requests for non-modifying operations like initiating a scrub on an OSD, ClusterMonitor
can skip the RequestFactory layer and construct a UserRequest directly before passing it
into RequestCollection.submit.

TODO: With #7174, use the command-type OSD operations as an example here.

2. Running a UserRequest object
-------------------------------

Once the request object has been constructed, it is ready to be executed.

Executing requests are contained in the RequestCollection class, each
ClusterMonitor has one of these.  They are added in RequestCollection.submit,
which adds the request to the collection and invokes its submit() method.

The `submit` call sends the ceph commands to a named minion.  This is at
the discretion of the caller, but is currently always the 'favorite' minion
of a ClusterMonitor.  `submit` returns immediately: all the UserRequest methods
are non-blocking and responses are handled in separate calls.

The ClusterMonitor event loop detects salt job completion events, and passes
them to RequestCollection.  RequestCollection looks up the request (it keeps
a map of JID to request) and invokes the `complete_jid` member of UserRequest.

`complete_jid` may be the end of the story, in which case it would call `complete`
to mark the request as done.  However, it may also start another job, or do
something else.  The "something else" may be waiting for cluster maps to update --
UserRequests are notified of changes to cluster maps in the `on_map` method.

3. Error handling
-----------------

If a salt job raises an exception, then `UserRequest.complete_jid` never sees it.  Instead,
RequestCollection marks the request as errored (with `set_error` calls `complete` on the request).

If a salt job dies without the calamari server receiving a response (for example, if the
minion spontanously restarts, or the minion and master are out of contact for an extended period) then
RequestCollection will eventually recognise this and mark the request as errored+complete.  In this
case the UserRequest itself is also never notified aside from the calls to set_error and complete.

Reference: the relevant classes
-------------------------------

.. autoclass:: cthulhu.manager.user_request.UserRequest

.. autoclass:: cthulhu.manager.rpc.RpcInterface

.. autoclass:: cthulhu.manager.cluster_monitor.ClusterMonitor

.. autoclass:: cthulhu.manager.pool_request_factory.PoolRequestFactory

.. autoclass:: cthulhu.manager.user_request.OsdMapModifyingRequest

.. autoclass:: cthulhu.manager.request_collection.RequestCollection
