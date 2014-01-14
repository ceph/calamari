.. Calamari REST API documentation master file, created by
   sphinx-quickstart on Tue Jan 14 15:44:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the Calamari REST API documentation
==============================================

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
- Refer to specific information about the available API :doc:`resources`

Contents
--------

.. toctree::
   :maxdepth: 2

   authentication
   conventions
   resources


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
