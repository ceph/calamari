
Conventions
===========

Asynchronous operations
-----------------------

When an operation may take some time, a ``202 ACCEPTED`` status is returned with a body containing
the request ID like this:

.. code-block:: json

    {'request_id': 'xxx'}

Usually ``PATCH`` operations will return this, although if the requested change is a no-op then
they may return ``304 NOT MODIFIED``.

Dates and times
---------------

Date/time fields in the API are always sent as timezone-aware ISO-8601 time strings
like ``2014-01-17T12:19:26.317355+00:00``.  Data structures passed through verbatim
from the Ceph cluster may leave off the timezone qualifier, and should be interpreted
as UTC.


Use of HTTP verbs
-----------------

Creations and destruction of objects is always done using appropriate ``POST`` and ``DELETE``
verbs.  ``GET`` requests are always read-only and do not have side effects.

The ``PATCH`` verb is preferred to ``PUT`` for modifying objects, because it allows API consumers to
be more specific about what they are changing and avoid unintended side effects.  Modifying an
object is

Cluster FSIDs and names
-----------------------

Calamari does not assume that cluster names are unique: since clusters are by default
always created with the name 'ceph', it is the unique FSID that is used both internally
and in the REST API to identify clusters.  This results in rather long URLs, but ensures
consistent behavior.

Server FQDNs and hostnames
--------------------------

In Calamari, servers are identified by their fully qualified domain name (FQDN) rather than
their hostname.  This is because hostnames are sometimes not unique within a site.  FQDNs are
not guaranteed to be unique either, but this is a more reasonable expectation and a common
one in configuration management software.

Pagination
----------

Some list views provide paginated responses for GETs.  These responses contain an object instead
of a list, where the list of results is in the ``results`` attribute and the total number of
objects available is in the ``count`` attribute.

To control the page returned and the page size returned, use the ``page`` (counting from 1) and
``page_count`` parameters respectively.  For example, the following contrived example returns
only the first two events for a cluster:

::

    GET api/v2/cluster/d530413f-9030-4daa-aba5-dfe3b6c4bb25/event?page=1&page_size=2

.. code-block:: json

    {
        "count": 20,
        "next": "http://localhost:8000/api/v2/cluster/d530413f-9030-4daa-aba5-dfe3b6c4bb25/event?page=2&page_size=2",
        "previous": null,
        "results": [
            {
                "when": "2014-01-16T22:18:37.133Z",
                "severity": "WARNING",
                "message": "Health of cluster 'ceph' degraded from HEALTH_OK to HEALTH_WARN"
            },
            {
                "when": "2014-01-16T22:18:37.131Z",
                "severity": "WARNING",
                "message": "OSD ceph.4 went down"
            }
        ]
    }