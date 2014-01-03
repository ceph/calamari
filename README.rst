

DEVELOPMENT BRANCH
==================

Calamari 2.0
============

Check out the `Architecture document`_ to get an idea of the overall
structure.

.. _Architecture document: https://docs.google.com/document/d/11Sq5UW3ZzeTwPBk3hPbrPI002ScycZQOzXPev7ixJPU/edit?usp=sharing


This code is meant to be runnable in two ways: in *production mode*
where it is installed systemwide from packages, or in *development mode*
where it us running out of a git repo somewhere in your home directory.

*In a hurry?* you don't have to follow the detailed development mode
installation instructions below if you use the vagrant setup in
``vagrant/devmode``.

Installing in production mode is not described here because the short
version is "follow the same instructions we give to users".  Installing
in development mode is intrinsically a bit custom, so here are some
pointers:


Installing dependencies
-----------------------

If you haven't already, install some build dependencies (apt, yum, brew, whatever) which
will be needed by the pip packages:

::

    sudo apt-get install python-virtualenv git python-dev swig libzmq-dev g++

If you're on ubuntu, there are a couple packages that are easier to install with apt
than with pip (and because of `m2crypto weirdness`_)

::

    sudo apt-get install python-cairo python-m2crypto

1. Create a virtualenv (if you are on ubuntu and using systemwide installs of
   cairo and m2crypto, then pass *--system-site-packages*)
2. Install dependencies with ``pip install -r requirements.txt``.
3. Install graphite and carbon, which require some special command lines:

::

    pip install carbon --install-option="--prefix=$VIRTUAL_ENV" --install-option="--install-lib=$VIRTUAL_ENV/lib/python2.7/site-packages"
    pip install git+https://github.com/jcsp/graphite-web.git@calamari --install-option="--prefix=$VIRTUAL_ENV" --install-option="--install-lib=$VIRTUAL_ENV/lib/python2.7/site-packages"


4. Grab the `GUI code <https://github.com/inktankstorage/clients>`_, build it and
   place the build products in ``webapp/content`` so that when it's installed you
   have a ``webapp/content`` directory containing ``admin``, ``dashboard`` and ``login``.

.. _m2crypto weirdness: http://blog.rectalogic.com/2013/11/installing-m2crypto-in-python.html

*Aside: unless you like waiting around, set PIP_DOWNLOAD_CACHE in your environment*

Getting ready to run
--------------------

Calamari server consists of multiple modules, link them into your virtualenv:

::

    pushd rest-api ; python setup.py develop ; popd
    pushd cthulhu ; python setup.py develop ; popd
    pushd minion-sim ; python setup.py develop ; popd
    pushd calamari-web ; python setup.py develop ; popd

Graphite needs some folders created:

::

    mkdir -p ${VIRTUAL_ENV}/storage/log/webapp
    mkdir -p ${VIRTUAL_ENV}/storage


The development-mode config files have some absolute paths that need rewriting in
a fresh checkout, there's a script for this:

::

    ~/calamari$ dev/configure.py
    Calamari repo is at: /home/vagrant/calamari, user is vagrant
    Writing /home/vagrant/calamari/dev/etc/salt/master
    Writing /home/vagrant/calamari/dev/calamari.conf
    Complete.  Now run:
     1. `CALAMARI_CONFIG=dev/calamari.conf calamari-ctl initialize`
     2. supervisord -c dev/supervisord.conf -n

Create the cthulhu service's database:

::

    CALAMARI_CONFIG=dev/calamari.conf calamari-ctl initialize


Running the server
------------------

The server processes are run for you by ``supervisord``.  A healthy startup looks like this:

::

    calamari john$ supervisord -n -c dev/supervisord.conf
    2013-12-02 10:26:51,922 INFO RPC interface 'supervisor' initialized
    2013-12-02 10:26:51,922 CRIT Server 'inet_http_server' running without any HTTP authentication checking
    2013-12-02 10:26:51,923 INFO supervisord started with pid 31453
    2013-12-02 10:26:52,925 INFO spawned: 'salt-master' with pid 31456
    2013-12-02 10:26:52,927 INFO spawned: 'carbon-cache' with pid 31457
    2013-12-02 10:26:52,928 INFO spawned: 'calamari-frontend' with pid 31458
    2013-12-02 10:26:52,930 INFO spawned: 'cthulhu' with pid 31459
    2013-12-02 10:26:54,435 INFO success: salt-master entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    2013-12-02 10:26:54,435 INFO success: carbon-cache entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    2013-12-02 10:26:54,435 INFO success: calamari-frontend entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
    2013-12-02 10:26:54,435 INFO success: cthulhu entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)

Supervisor will print complaints if something is not starting up properly.  Check in the various \*.log files to
find out why something is broken, or run processes individually by hand to debug them (see the commands in supervisord.conf).

At this point you should have a server up and running at ``http://localhost:8000/`` and
be able to log in to the UI.

Ceph servers
------------

Simulated minions
_________________

Impersonate some Ceph servers with the minion simulator:

::

    minion-sim --count=3




Real minions
____________

If you have a real live Ceph cluster, install ``salt-minion`` on each of the
servers, and configure it to point to your development instance host (mine is 192.168.0.5,
**substitute yours**)

::

    wget -O - https://raw.github.com/saltstack/salt-bootstrap/develop/bootstrap-salt.sh
    | sudo sh && echo "master: 192.168.0.5" >> /etc/salt/minion && service
    salt-minion restart

Allowing minions to join
________________________

Authorize the simulated salt minions to connect to the calamari server:

::

    salt-key -c dev/etc/salt -L
    salt-key -c dev/etc/salt -A

You should see some debug logging in cthulhu.log, and if you visit /api/v1/cluster in your browser
a Ceph cluster should be appear.

Further reading (including running tests)
-----------------------------------------

Build the docs:

::

    cd docs/
    make html
    open _build/html/index.html
