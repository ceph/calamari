import time


class WaitTimeout(Exception):
    pass


def wait_until_true(condition, timeout=10):
    i = 0
    while not condition():
        if i >= timeout:
            raise WaitTimeout("After %s seconds" % i)
        i += 1
        time.sleep(1)
