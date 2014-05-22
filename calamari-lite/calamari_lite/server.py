
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
from gevent.wsgi import WSGIServer
from cthulhu.manager.manager import Manager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")


class ShallowCarbonCache(gevent.Greenlet):
    def __init__(self):
        super(ShallowCarbonCache, self).__init__()
        self.complete = gevent.event.Event()
        self.latest = {}

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

                    i[stat_path[-1]] = val

        server = StreamServer(('0.0.0.0', 2003), stream_handle)
        server.start()
        self.complete.wait()
        server.stop()

    def stop(self):
        self.complete.set()


def main():
    # Instruct salt to use the gevent version of ZMQ
    import zmq.green
    import salt.utils.event
    salt.utils.event.zmq = zmq.green

    carbon = ShallowCarbonCache()
    carbon.start()

    cthulhu = Manager()
    cthulhu.start()

    app = get_internal_wsgi_application()
    wsgi = WSGIServer(('0.0.0.0', 8002), app)
    wsgi.start()

    complete = gevent.event.Event()

    def shutdown():
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        cthulhu.on_tick()
        complete.wait(timeout=5)
