
Testing
=======

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

In Calamari server tests we saw the test suite executing against a cluster simulator,

In this section we'll configure those same tests to run against a real cluster built
on teuthology.

Step 0: get your ssh credentials into this environment

Step 0.5 lock some nodes?

Step 1: building the cluster

.. code-block:: bash

    cd /home/vagrant/teuthology
    source virtualenv/bin/activate
    teuthology $ teuthology --archive ~/gmeno/archive10 --owner vagrant@ubuntu --machine-type mira --description "Gregory.Meno@inktank.com ceph-deploy interactive" ~/gmeno/ceph-deploy2.yaml

If successfull this will leave you in an interactive state.
Check by ssh and running ceph -w

Step 2: kickoff tests
nosetests something
TBD

Teardown: Hit Ctrl-D in the teuthology session

Troubleshooting:

.. code-block:: bash

  1 #!/bin/bash
  2
  3 set -x
  4 set -e
  5
  6 for host in $@
  7 do
  8     ssh plana01 "sudo cobbler system edit --name=${host} --netboot on"
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
