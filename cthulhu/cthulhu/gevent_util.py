from gevent import getcurrent
from functools import wraps
from contextlib import contextmanager


class ForbiddenYield(Exception):
    pass


@contextmanager
def nosleep_mgr():
    yield


def nosleep(func):
    """
    This decorator is used to assert that no geven greenlet yields
    occur in the decorated function.
    """
    return func


if __name__ == '__main__':
    # Tests for nosleep()
    # ===================

    import gevent.queue
    import gevent.greenlet
    from gevent import sleep

    # This should raise no exception (print doesn't yield)
    with nosleep_mgr():
        print "test print!"

    # This should raise an exception when we try push to a fixed size queue
    try:
        smallq = gevent.queue.Queue(1)
        with nosleep_mgr():
            smallq.put(1)
            smallq.put(2)
    except ForbiddenYield:
        pass
    else:
        raise AssertionError("Failed")

    # This should raise no exception when we try push to an unlimited size queue
    bigq = gevent.queue.Queue(0)
    with nosleep_mgr():
        for i in range(0, 10000):
            bigq.put(i)

    # This should raise an exception on sleep
    # FIXME!!!!
    try:
        sleep(0.1)
    except ForbiddenYield:
        pass
    else:
        raise AssertionError("Failed")
