
"""
A lightweight server for running a minimal Calamari instance
in a single process.
"""

from django.core.servers.basehttp import get_internal_wsgi_application
import gevent.event
import gevent
import signal
from gevent.server import StreamServer
import os
from gevent.pywsgi import WSGIServer
import zerorpc
from calamari_common.config import CalamariConfig
from cthulhu.log import log
import sys
from gevent.hub import Hub
import ssl as _ssl
config = CalamariConfig()


TIMEOUT = 5  # seconds till we tick the cthulhu eventer
SALT_RESET_PERIOD = 300  # seconds till we teardown/setup our salt_caller. Do this because it's leaking memory


def patch_gevent_hub_error_handler():

    Hub._origin_handle_error = Hub.handle_error

    def custom_handle_error(self, context, type, value, tb):
        if not issubclass(type, Hub.SYSTEM_ERROR + Hub.NOT_ERROR):
            log.error("Uncaught exception", exc_info=(type, value, tb))

        self._origin_handle_error(context, type, value, tb)

    Hub.handle_error = custom_handle_error


patch_gevent_hub_error_handler()


def handle_exception(exc_type, exc_value, exc_traceback):
    log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")

ssl = {
    'certfile': config.get('calamari_web', 'ssl_cert'),
    'keyfile': config.get('calamari_web', 'ssl_key')
}

# Force TLS if calamari is configured to do so
if config.get('calamari_web', 'force_tls'):
    ssl['ssl_version'] = _ssl.PROTOCOL_TLSv1

class ShallowCarbonCache(gevent.Greenlet):
    def __init__(self):
        super(ShallowCarbonCache, self).__init__()
        self.complete = gevent.event.Event()
        self.latest = {}

        self.rpc = zerorpc.Server({
            'get_latest': self.get_latest
        })

        self.rpc_thread = None

    def get_latest(self, paths):
        result = {}
        import json
        print json.dumps(self.latest, indent=2)

        for path in paths:
            i = self.latest
            for p in path.split("."):
                try:
                    i = i[p]
                except KeyError:
                    break

            if isinstance(i, float):
                result[path] = i
            else:
                result[path] = None

        return result

    def start(self):
        super(ShallowCarbonCache, self).start()

        self.rpc.bind("tcp://127.0.0.1:5051")  # TODO config setting
        self.rpc_thread = gevent.spawn(lambda: self.rpc.run())

    def _run(self):
        def stream_handle(socket, address):
            f = socket.makefile()
            while True:
                line = f.readline()
                if not line:
                    break
                else:
                    stat, val, t = line.strip().split()
                    stat_path = stat.split(".")
                    i = self.latest
                    for p in stat_path[:-1]:
                        if p not in i:
                            i[p] = {}
                        i = i[p]

                    i[stat_path[-1]] = float(val)

        server = StreamServer(('0.0.0.0', 2003), stream_handle)
        server.start()
        self.complete.wait()
        server.stop()

    def stop(self):
        self.complete.set()
        if self.rpc_thread:
            self.rpc_thread.stop()


def main():

    log.info('calamari-list: starting')
    complete = gevent.event.Event()
    ceph_argparse = None
    while not ceph_argparse:
        try:
            import ceph_argparse
        except ImportError:
            log.error('Cannot import ceph_arg_parse module -- please install ceph')
            complete.wait(timeout=50)

    from cthulhu.manager.manager import Manager

    carbon = ShallowCarbonCache()
    carbon.start()

    cthulhu = Manager()
    cthulhu_started = False

    while not cthulhu_started:
        try:
            if not cthulhu_started:
                cthulhu_started = cthulhu.start()

        except Exception, e:
            log.exception('It borked')
            log.error(str(e))
            complete.wait(timeout=5)

    app = get_internal_wsgi_application()
    wsgi = WSGIServer(('0.0.0.0', 8002), app, **ssl)
    wsgi.start()

    def shutdown():
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    x = 0
    while not complete.is_set():
        cthulhu.eventer.on_tick()
        complete.wait(timeout=TIMEOUT)
        if x > SALT_RESET_PERIOD:
            cthulhu.eventer.reset_event_sink()
            x = 0
        x += TIMEOUT
    wsgi.stop()
