
Logging
=======

Location of logs
----------------

Logs for calamari and supporting components are located in /var/log/calamari

How long logs are kept
----------------------
In production logs are rotated daily and kept for seven days.

Summary of log file contents
----------------------------

- http_access.log - information about http requests
- http_error.log  - what errors the http server handles
- calamari.log - contains information about cluster monitors and errors in the API layer
- cthulhu.log - contains information about the state of the ceph-clusters that it has been configured to know about


Troubleshooting
---------------

calamari.log and cthulhu.log operate in production at a level of low verbosity.
This behaviour can be changed by editing:

.. code-block:: bash

    /etc/calamari/calamari.conf

to set

.. code-block:: python

    log_level = DEBUG

Then restart the services that the config has been modified for.
