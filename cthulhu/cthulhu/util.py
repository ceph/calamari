import datetime

from dateutil import tz
import gevent.greenlet
import gevent.event


def now():
    """
    A tz-aware now
    """
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())


class Ticker(gevent.greenlet.Greenlet):
    def __init__(self, period, callback, *args, **kwargs):
        super(Ticker, self).__init__(*args, **kwargs)
        self._period = period
        self._callback = callback
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def _run(self):
        while not self._complete.is_set():
            self._callback()
            self._complete.wait(self._period)
