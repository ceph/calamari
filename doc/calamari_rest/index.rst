
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

Contents
--------

.. toctree::
   :maxdepth: 2

   authentication
   conventions
   resources/resources
