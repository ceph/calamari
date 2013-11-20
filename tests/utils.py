import time


class WaitTimeout(Exception):
    pass


def wait_until_true(condition, timeout=10):
    elapsed = 0
    period = 1
    while not condition():
        if elapsed >= timeout:
            raise WaitTimeout("After %s seconds" % elapsed)
        elapsed += period
        time.sleep(period)
    return elapsed
