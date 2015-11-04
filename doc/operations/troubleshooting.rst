
Troubleshooting Calamari Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note: the guidance here is about troubleshooting the Calamari monitoring layer, not
Ceph in general, see the `ceph documentation <https://ceph.com/docs/master/>`_ for
more general issues.

I have followed the instructions in :doc:`minion_connect`, but my servers are
=============================================================================
not appearing in the Calamari User Interface
============================================

* Check that ``/etc/salt/minion.d/calamari.conf`` on the Ceph server specifies
  the correct address for the Calamari server.
* Check for errors in ``/var/log/salt/minion`` on the Ceph server.

My Ceph cluster has been detected by Calamari, but some of the dashboard
========================================================================
widgets like IOPs and Usage are blank
=====================================

* Check that the Calamari version of diamond is installed on all the Ceph
  servers acting as mons.
* Using your web browser, visit the graphite dashboard at ``/graphite/dashboard/``
  on the Calamari server.  Check that statistics with paths starting ``ceph.cluster``
  are present.

The Calamari user interface is displaying a 500 error
=====================================================

* Check ``/var/log/calamari/calamari.log`` for a detailed error message and
  backtrace, and seek help via the mailing list or issue tracker.


.. _get-logs:

The Calamari API is returning an HTTP 500 error
===============================================

* Run ``tail -f /var/log/calamari/*``
* Re-request the resource that is erroring.
* include all output from the tail command when asking for help

I tried tail -f on the logs and I'm not seeing much
===================================================

* set ``log_level = DEBUG`` for services listed in ``/etc/calamari/calamari.conf``
* restart these services with 

.. code-block:: bash

    sudo supervisorctl restart cthulhu
    sudo service apache2 restart  # initd systems
    sudo systemctl httpd restart  # systemd systems

* repeat steps in :ref:`get-logs`
