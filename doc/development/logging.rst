
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

Increase the log level of services in ``/etc/calamari/calamari.conf`` with the ``cthulhu.log_level``
and ``calamari_web.log_level`` settings.  You can see the log paths in the same config file.  You usually
want 'debug' level, but don't forget to turn it back to 'warn' when you're done.

After changing the level, restart the services:

::

    sudo supervisorctl restart cthulhu
    sudo service apache2 restart

For ultra-mega SQL verbosity you can also set cthulhu.db_log_level
