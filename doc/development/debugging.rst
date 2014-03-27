
Debugging Calamari
==================

Instructions here are for ubuntu, reader is assumed to be technical enough to know the
Red Hat equivalents.

Logs
----

Always increase the log verbosity before going further.  See :doc:`logging`.


Manhole
-------

The cthulhu service uses manhole in oneshot mode.  Sending a USR1 signal will pause execution
and cause it to listen for connections on a socket at /tmp/manhole-<PID>.

Connect to the socket using ``socat`` (not part of default installs but widely available) like this:

::

    sudo kill -USR1 <pid>
    sudo socat readline unix-connect:/tmp/manhole-<pid>

manhole doesn't seem to work on OS X, this is mainly for debugging systems running
in production mode.

To get backtraces of all running greenlets, do this:

::

    >>> from cthulhu.manager import dump_stacks
    >>> dump_stacks()


Note that while you are at the interactive console, all other execution is paused: when
you Ctrl-D the console, execution will resume.

Resource statistics
-------------------

Cthulhu sends statistics about its own process to carbon.  They're named calamari.cthulhu.<stat>
where <stat> is one of the fields from python's built in resource.getrusage -- see python and
UNIX docs for more info on what the stats mean.


Direct graphite access
----------------------

For plotting calamari's internal stats or examining ceph stats that the GUI doesn't expose,
you can access a vanilla graphite dashboard UI at ``/graphite/dashboard`` on the same
port as the REST API.
