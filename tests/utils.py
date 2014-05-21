import time
import datetime
from tests.config import TestConfig

config = TestConfig()


def get_timeout_scaling_factor():
    factor = 1
    if config.get('testing', 'ceph_control') == 'external':
        factor = config.get('testing', 'external_timeout_factor')
    elif config.get('testing', 'ceph_control') == 'embedded':
        factor = config.get('testing', 'embedded_timeout_factor')
    return factor


class WaitTimeout(Exception):
    pass


def wait_until_true(condition, timeout=10):
    elapsed = 0
    period = 1
    while not condition():
        if elapsed >= timeout:
            raise WaitTimeout("After %s seconds (at %s)" % (elapsed, datetime.datetime.utcnow().isoformat()))
        elapsed += period
        time.sleep(period)
    return elapsed


def scalable_wait_until_true(condition, timeout=10):
    timeout = timeout * get_timeout_scaling_factor()
    return wait_until_true(condition, timeout)


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper
