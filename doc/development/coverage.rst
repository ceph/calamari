
Code coverage
=============

Procedure
---------

1. Ensure that you have the `coverage` module installed.
2. Create a `sitecustomize.py` file in your virtualenv's site-packages folder, containing:

::

    import coverage
    coverage.process_startup()

3. Set the `COVERAGE_PROCESS_START` environment variable

::

    calamari $ export COVERAGE_PROCESS_START=`pwd`/coverage.conf

4. Run your Calamari server in the shell where you've got `COVERAGE_PROCESS_START` set:

::

    calamari $ supervisord -c ./supervisord.conf -n

5. At some point in the future, Ctrl-C your supervisor instance.  Coverage should have
   left a bunch of `.coverage.<hostname>.<pid>.<time>` files behind.

6. Run `coverage combine` to generate one `.coverage` file from the per-process files.

7. Run `coverage html` to generate a report in `htmlcov`, and open htmlcov/index.html

Caveats
-------

- The coverage module does not always play nicely with gevent.  Especially, you will
  sometimes see false-negatives, where a line such as a ZeroRPC client call is green,
  and subsequent lines are red even though you know they were reached.

- The 'runserver' process doesn't currently generate any coverage output when run
  from supervisord.conf, it's something about how supervisor is kiling it.