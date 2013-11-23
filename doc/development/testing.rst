
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

Unit tests
----------

On a module by module basis, in tests/ within a module.