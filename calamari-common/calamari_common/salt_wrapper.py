
"""
Wrap all our salt imports into one module.  We do this
to make it clear which parts of the salt API (or internals)
we are touching, and to make it easy to globally handle a
salt ImportError e.g. for building docs in lightweight
environment.
"""


import gevent
import logging


try:
    try:
        from salt.client import condition_kwarg
    except ImportError:
        # Salt moved this in 382dd5e
        from salt.utils.args import condition_input as condition_kwarg

    from salt.client import LocalClient  # noqa
    from salt.utils.event import MasterEvent  # noqa
    from salt.key import Key  # noqa
    from salt.config import master_config  # noqa
    from salt.utils.master import MasterPillarUtil  # noqa
    from salt.config import client_config  # noqa
    from salt.loader import _create_loader
except ImportError:
    condition_kwarg = None
    LocalClient = None
    MasterEvent = None
    Key = None
    master_config = None
    MasterPillarUtil = None
    client_config = lambda x: None
    _create_loader = None


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

    def __init__(self, logger, config):
        """
        :param config: a salt client_config instance
        """
        # getChild isn't in 2.6
        self._log = logging.getLogger('.'.join((logger.name, 'salt')))
        self._silence_counter = 0
        self._config = config
        self._master_event = MasterEvent(self._config['sock_dir'])

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
                self._log.warning("Re-opening connection to salt-master")

                self._silence_counter = 0
                # Re-open the connection as a precaution against this lack of
                # messages being a symptom of a connection that has gone bad.
                old_ev = self._master_event
                gevent.spawn(lambda: self._destroy_conn(old_ev))
                self._master_event = MasterEvent(self._config['sock_dir'])
        else:
            self._silence_counter = 0
            return ev
