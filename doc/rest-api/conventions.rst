
Conventions
===========

Asynchronous operations
-----------------------

When an operation may take some time, a ``204 ACCEPTED`` status is returned with a body containing
the request ID like this:

.. code-block:: json

    {'request_id': 'xxx'}

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
