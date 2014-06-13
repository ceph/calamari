
Installing Calamari Server on Ubuntu 12.04
==========================================

These instructions explain how to install Calamari server.  Note that
these instructions are for the single central Calamari server, not for
the Ceph servers you will connect (see :doc:`minion_connect`).

.. note::

    These instructions are for Ubuntu, but the general procedure will be the same
    for any other linux distribution for which you have successfully built Calamari
    packages.

Prerequisites
-------------

* An internet connection to download dependencies
* ``.deb`` packages for calamari-server and calamari-clients (see :doc:`/development/building_packages`)

Installing dependencies
-----------------------

Follow the instructions at http://docs.saltstack.com/en/latest/topics/installation/ubuntu.html
to enable the SaltStack PPA package repository and install the ``salt-master`` and ``salt-minion``
packages.

Install the remaining dependencies using ``apt``:

::

    sudo apt-get update && sudo apt-get install -y apache2 libapache2-mod-wsgi libcairo2 supervisor python-cairo libpq5 postgresql   


Installing Calamari Server
--------------------------

Install the ``calamari-server`` and ``calamari-clients`` packages using ``dpkg``:

::

    sudo dpkg -i calamari-server*.deb calamari-clients*.deb

Run the following command to complete installation:

::

    sudo calamari-ctl initialize

Finally, open your web browser and visit the address of your Calamari server
to log into the Calamari user interface.

Optional: installing minion package repository
----------------------------------------------

The Calamari server can optionally act as a package repository for the Ceph
servers in the system.

If you have a built minion repository file, it will be named something
like ``calamari-repo-ubuntu.tar.gz``.  To install this, simple extract
it in ``/opt/calamari/webapp/content`` and rename it to ``calamari-minions``.
You don't have to call this repo ``calamari-minions``, but it won't match the
instructions in :doc:`minion_connect` if you don't.

::

    cd /opt/calamari/webapp/content
    tar zxf ~/calamari-repo-ubuntu.tar.gz
    mv ubuntu calamari-minions

