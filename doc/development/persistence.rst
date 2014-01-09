
Persistence in Calamari
=======================

Calamari persists things to disk when:

- They're too big to keep in RAM
- We need them to survive a service restart

In general the REST API gets data from running services via RPC rather than
from the database.

In the web frontend
-------------------

The web frontend (calamari-web and rest-api) use a Django database, which
contains the Session, User and Group models.  This is tiny and low traffic,
although it does incur a write on every HTTP request because of Django
touching the session token.

In graphite
-----------

Graphite stores WhisperDB files on the local filesystem, in a location specified
in carbon.conf (so carbon-cache knows where to write to) and calamari.conf (so
graphite knows where to read from).  carbon-cache writes to these files, and
graphite reads from them.

In cthulhu
----------

The ServerMonitor and ClusterMonitor
classes both maintain a full in-memory view of the system, but we don't want to have to
wait for servers to report in to regenerate this when cthulhu restarts, and we sometimes
want to persist some history too.

Rather than calling out to the database from within event handlers, persistence operations
are pushed to a queue, which is serviced by the Persister class.

- We want cthulhu RPCs and event handlers to be as snappy as possible, and not
  block on any I/O to e.g. postgres.
- Actually doing persistence requires I/O, so would cause event handler greenlets
  to sleep, requiring them to do locking to protect any resources they're in
  the process of modifying.
- It enforces a rigorous separation of persistence from business logic, such that
  we could even turn off persistence at will and the monitoring would continue
  to function (albeit without the nice recovery on restart).

.. autoclass:: cthulhu.persistence.persister.Persister

.. automodule:: cthulhu.persistence.sync_objects
   :members:

.. automodule:: cthulhu.persistence.servers
   :members:
