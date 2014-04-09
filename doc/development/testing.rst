
Testing
=======

.. _calamari-server-tests:

Calamari server tests
---------------------

These are end to end tests of the Calamari server as a black box, with
a Ceph cluster in one end and REST out the other.

Highlights:

- Using unittest2 (the variant bundled in django), because although not everything
  is a unit test, a library that runs functions and reports results is a handy thing.
- `nose` is a handy utility for finding and running tests

Assuming you've already got a nice development environment set up (such that
you can run Calamari services with supervisor without errors), you can execute
the server tests very simply:

.. code-block:: bash

    calamari $ nosetests tests/

Note that these take some time to execute: since these are not unit tests, they
incur lots of the real-life overheads of a full blown system, and some tests
incur walltime waits to exercise certain paths.

Testing against a real live ceph cluster
----------------------------------------

In :ref:`calamari-server-tests` we saw the test suite executing against a cluster simulator,

In this section we'll configure those same tests to run against a real cluster built
on teuthology.

Theory of operation
^^^^^^^^^^^^^^^^^^^

We will build a ceph cluster using the ceph-deploy task on teuthology. Teuthology is a framework that allocates
and provisions hardware for testing. ceph-deploy is a piece of software that simplifies setup
of ceph clusters. Once the cluster is up and reports healthy we will use our devmode instance of calamari to
execute the :ref:`calamari-server-tests`. Finally we will teardown the cluster.

Teuthology is typically used in a fashion that trades speed for isolation. Tasks that install packages are expected to
remove everything it installs. This can leave lab machines in an inconsistent state.
See :ref:`troubleshooting` below for a process to reimage machines.

Step 0: Setup SSH credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

get your ssh credentials into this environment and setup VPN
There are many ways to accomplish this and it is beyond the scope of this document

Test that you have a working step 0:

.. code-block:: bash

    ssh ubuntu@teuthology.front.sepia.ceph.com "echo 'it works'"

Step 1: Building the cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Please replace calamari@inktank.com with your email address
    cd /home/vagrant/teuthology
    source virtualenv/bin/activate
    rm -rf archive; teuthology --archive archive \
                    --lock \
                    --owner calamari@inktank.com \
                    --machine-type mira \
                    --description "calamari devmode test target" \
                    ~/calamari/dev/teuthology.yaml

If successful this will leave you in an interactive state. Which looks like this:

.. code-block:: python

    Ceph test interactive mode, use ctx to interact with the cluster, press control-D to exit...
    >>>


Test that you have a working step 1:

.. code-block:: bash

    cd /home/vagrant/teuthology
    source virtualenv/bin/activate
    grep -o "^.*\.front\.sepia\.ceph\.com" archive/config.yaml |\
        xargs -I'{}' ssh '{}' "if [ -e /etc/ceph/ceph.client.0.keyring ]; then ceph health; fi"


Step 2: Testing setup
^^^^^^^^^^^^^^^^^^^^^

There are a few manual changes you'll need to make to test against this cluster:
- Add a master_fqdn dict to teuthology/archive/cluster.yaml like:
.. code-block:: yaml
    master_fqdn:
        <FQDN of the machine where you are running a calmari devmode instance>

- Edit dev/calamari.conf changing ceph_control under testing to 'external'
.. code-block:: yaml
    [testing]
        ceph_control = external

- Make sure you have the repositories setup so that bootstrap can succeed TODO

Step 2: Kickoff tests
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # TODO this will be connected up in http://tracker.ceph.com/issues/7812
    cd calamari
    source env/bin/activate
    nosetests tests/


.. _teardown:

Step 3: Teardown
^^^^^^^^^^^^^^^^

Hit Ctrl-D in the teuthology session

.. code-block:: bash

    # Please replace calamari@inktank.com with your email address
    cd /home/vagrant/teuthology
    source virtualenv/bin/activate
    teuthology-lock --list-targets --owner calamari@inktank.com |\
     teuthology-nuke -t /dev/stdin -ru --owner=calamari@inktank.com

.. _troubleshooting:

Troubleshooting
^^^^^^^^^^^^^^^

If you see something like this try running the code in :ref:`teardown`

.. code-block:: bash

    INFO:teuthology.run:Summary data:
    {description: calamari devmode test target, failure_reason: 'Stale jobs detected,
        aborting.', owner: calamari@inktank.com, success: false}


{description: calamari devmode test target, failure_reason: not enough machines are
    available, owner: calamari@inktank.com, success: false}

WARNING: This should only be performed on machines you have locked previously.

.. code-block:: bash

  1 #!/bin/bash
  2
  3 set -x
  4 set -e
  5
  6 for host in $@
  7 do
  8     ssh ubuntu@plana01.front.sepia.ceph.com "sudo cobbler system edit --name=${host} --netboot on"
  9     /usr/local/bin/ipmitool -H ${host}.ipmi.sepia.ceph.com -I lanplus -U inktank -P ApGNXcA7 power reset
 10 done;

you can add a —profile argument to the cobbler command to select distro
and do a "sudo cobbler profile list" on plana01 to see what's available


Unit tests
----------

On a module by module basis, in tests/ within a module.  For example, in ``cthulhu``:

.. code-block:: bash

    calamari $  nosetests cthulhu/tests
    ........
    ----------------------------------------------------------------------
    Ran 8 tests in 0.288s

    OK
