
import gevent.greenlet
import gevent.event
import json

try:
    import zmq
except ImportError:
    zmq = None


class NotificationThread(gevent.greenlet.Greenlet):
    """
    Responsible for:
     - Listening for Websockets clients connecting, and subscribing them
       to the ceph: topics
     - Publishing messages to Websockets topics on behalf of other
       python code.
    """
    def __init__(self):
        super(NotificationThread, self).__init__()

        if zmq is None:
            raise RuntimeError("zmq module not found")

        self._complete = gevent.event.Event()
        self._pub = None
        self._ready = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def publish(self, topic, message):
        self._ready.wait()
        self._pub.send(b'publish', zmq.SNDMORE)
        self._pub.send(topic, zmq.SNDMORE)
        self._pub.send(json.dumps(message))

    def _run(self):
        ctx = zmq.Context(1)
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://172.16.79.128:7002')
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        self._pub = ctx.socket(zmq.PUB)
        self._pub.connect('tcp://172.16.79.128:7003')
        self._ready.set()
        while not self._complete.is_set():
            try:
                parts = sub.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                self._complete.wait(timeout=1)
                continue

            if parts[1] == b'connect':
                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:completion')

                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:sync')
