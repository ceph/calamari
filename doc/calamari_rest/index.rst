
Calamari REST API documentation
===============================

Purpose
-------

This section explains the Calamari REST API, for developers building
software on top of it.  This might include user interfaces, scripts, or
plugins for third party management platforms.

Introduction
------------

The Calamari REST API provides access to detailed Ceph monitoring information and management operations
for third party applications.  This is the same API that the Calamari UI uses.

The Calamari REST API is distinct from the Ceph REST API: while the Ceph REST API provides low level
access to RADOS within one Ceph cluster, the Calamari REST API provides a higher level view of the
entire system.

To get started:

- Learn how to perform :doc:`authentication` with the Calamari REST API and write a simple client
- Learn about the :doc:`conventions` used
- Refer to specific information about the available API :doc:`resources/resources`

How to update this documentation
--------------------------------

While updates directly to ``.rst`` files will be immediately incorporated into the next
build of this documentation, the auto-generated portions require an extra step to reflect
changes in the code.  The ``docs`` target in the top level Makefile takes care of this: it
requires a fully configured development environment, and requires that some of the integration
tests (the top level ``tests/``) are in a passing state, as these are used to generate the API
examples.

In summary, when you have made a code change that you want to be reflected in the API, run ``make docs``
at the top level and commit the resulting changes to the ``doc/calamari_rest/resources/`` directory.

Contents
--------

.. toctree::
   :maxdepth: 2

   authentication
   conventions
   resources/resources
