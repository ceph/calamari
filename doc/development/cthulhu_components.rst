
Cthulhu components
==================

This page is about the internal makeup of the Cthulhu service.

An instance of the ``cthulhu-manager`` process consists of a ``Manager`` and
its children.  ``Manager`` consumes salt events, and so may its children.

gevent is used throughout: see :doc:`cthulhu_locking`.

Manager
-------

.. autoclass:: cthulhu.manager.manager.Manager
   :members:

RpcInterface
------------

.. autoclass:: cthulhu.manager.rpc.RpcInterface
   :members:

ServerMonitor
-------------

.. autoclass:: cthulhu.manager.server_monitor.ServerMonitor
   :members:

ClusterMonitor
--------------

.. autoclass:: cthulhu.manager.cluster_monitor.ClusterMonitor
   :members:

Eventer
-------

.. autoclass:: cthulhu.manager.eventer.Eventer
   :members:

Persister
---------

See :doc:`persistence`.

PluginMonitor
-------------

TODO: this will be the component that loads and executes plugins.

Notifier
--------

TODO: this will be the component that generates notifications for the UI
to be forwarded via websockets/ZeroGW.  Like Persister, this is something
that the other components send "fire and forget" messages to.
