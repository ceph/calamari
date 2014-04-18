import time
import datetime
from tests.config import TestConfig

config = TestConfig()


def get_timeout():
    timeout = config.get('testing', 'embedded_wait_timeout')
    if config.get('testing', 'ceph_control') == 'external':
        timeout = config.get('testing', 'external_wait_timeout')

    return timeout


class WaitTimeout(Exception):
    pass


def wait_until_true(condition, timeout=get_timeout()):
    elapsed = 0
    period = 1
    while not condition():
        if elapsed >= timeout:
            raise WaitTimeout("After %s seconds (at %s)" % (elapsed, datetime.datetime.utcnow().isoformat()))
        elapsed += period
        time.sleep(period)
    return elapsed


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper
