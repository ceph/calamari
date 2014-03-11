import time
import datetime


class WaitTimeout(Exception):
    pass


def wait_until_true(condition, timeout=20):
    elapsed = 0
    period = 1
    while not condition():
        if elapsed >= timeout:
            raise WaitTimeout("After %s seconds (at %s)" % (elapsed, datetime.datetime.utcnow().isoformat()))
        elapsed += period
        time.sleep(period)
    return elapsed
