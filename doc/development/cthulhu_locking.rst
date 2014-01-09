
Locking and gevent in cthulhu
=============================

Where are the locks?
--------------------

Cthulhu uses gevent, so instead of POSIX threads, concurrency is handled
with lightweight threads (greenlets) within a single OS thread.  This
allows us to avoid the need for locking on shared data structures, as long
as we're a little bit careful to avoid switching between greenlets partway
through functions.

The ClusterMonitor and ServerMonitor classes are both built as event
handlers/generators, handling incoming events (like those from
salt) and generating outgoing salt messages or Persister messages.  In
this model, all that's required for safety is that none of the event handling
functions is interrupted part way through, and that's easy to provide
because the handlers never do any IO themselves.

One exception to the 'no locks' rule is in UserRequests, which does I/O to
the salt master (to create jobs) during its calls.   This has a lock to protect
against the scenario where we call out to salt master to create a job, go to
sleep, and receive the job's result from a minion before we've received the
master's acknowledgement of our job creation.

The ``nosleep`` decorator
-------------------------

To ensure that subtle bugs don't creep in with unwanted greenlet yields
in regions that aren't meant to do any, the ``@nosleep`` decorator is used.

.. automodule:: cthulhu.gevent_util
   :members: nosleep