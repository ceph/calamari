import datetime

from dateutil import tz
import gevent.greenlet
import gevent.event
from cthulhu.log import log

import salt.utils.event


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


class SaltEventSource(object):
    """
    A wrapper around salt's MasterEvent class that closes and re-opens
    the connection if it goes quiet for too long, to ward off mysterious
    silent-death of communications (#8144)
    """

    # Not a logical timeout, just how long we stick inside a get_event call
    POLL_TIMEOUT = 5

    # After this long without messages, close and reopen out connection to
    # salt-master.  Don't want to do this gratuitously because it can drop
    # messages during the cutover (lossiness is functionally OK but user
    # might notice).
    SILENCE_TIMEOUT = 20

    def __init__(self, config):
        """
        :param config: a salt client_config instance
        """
        self._silence_counter = 0
        self._config = config
        self._master_event = salt.utils.event.MasterEvent(self._config['sock_dir'])

    def _destroy_conn(self, old_ev):
        old_ev.destroy()

    def get_event(self, *args, **kwargs):
        """
        Wrap MasterEvent.get_event
        """
        ev = self._master_event.get_event(self.POLL_TIMEOUT, *args, **kwargs)
        if ev is None:
            self._silence_counter += self.POLL_TIMEOUT
            if self._silence_counter > self.SILENCE_TIMEOUT:
                log.warning("Re-opening connection to salt-master")

                self._silence_counter = 0
                # Re-open the connection as a precaution against this lack of
                # messages being a symptom of a connection that has gone bad.
                old_ev = self._master_event
                gevent.spawn(lambda: self._destroy_conn(old_ev))
                self._master_event = salt.utils.event.MasterEvent(self._config['sock_dir'])
        else:
            self._silence_counter = 0
            return ev
