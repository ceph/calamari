Status
======

Builds
------

.. image:: https://travis-ci.org/Tendrl/ceph_bridge.svg?branch=master
    :target: https://travis-ci.org/Tendrl/ceph_bridge

Code Coverage
-------------

.. image:: https://coveralls.io/repos/github/Tendrl/ceph_bridge/badge.svg?branch=master
    :target: https://coveralls.io/github/Tendrl/ceph_bridge?branch=master


Testing
=======

Please, don't hesitate to write tests ;)


Unit tests
----------

*Files: /tests/unit/**

The goal of unit tests is to ensure that internal parts of the code work properly.
All internal methods should be fully covered by unit tests with a reasonable mocks usage.


About Tendrl unit tests:

- All `unit tests <http://en.wikipedia.org/wiki/Unit_testing>`_ are located inside /tests/unit/*
- Tests are written on top of: *testtools* and *mock* libs
- `Tox <https://tox.readthedocs.org/en/latest/>`_ is used to run unit tests


To run unit tests locally::

  $ pip install tox
  $ tox

To run py26, py27 or pep8 only::

  $ tox -e <name>

  #NOTE: <name> is one of py26, py27 or pep8

To get test coverage::

  $ tox -e cover

  #NOTE: Results will be in /cover/index.html

To generate docs::

  $ tox -e docs

  #NOTE: Documentation will be in doc/source/_build/html/index.html

Functional tests
----------------

*Files: /tests/functional/**

The goal of `functional tests <https://en.wikipedia.org/wiki/Functional_testing>`_ is to check that everything works well together.
Fuctional tests use Tendrl API only and check responses without touching internal parts.

To run functional tests locally::

  $ tox -e functional

Tendrl CI scripts
----------------

*Files: /tests/ci/**

This directory contains scripts and files related to the Tendrl CI system.

Tendrl Style Commandments
------------------------

*File: /tests/hacking/checks.py*

This module contains Tendrl specific hacking rules for checking commandments.