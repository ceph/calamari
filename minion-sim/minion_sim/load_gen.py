import random
import threading


class LoadGenerator(threading.Thread):
    def __init__(self, cluster):
        super(LoadGenerator, self).__init__()

        self._cluster = cluster
        self._complete = threading.Event()

    def run(self):
        interval = 0.5

        while not self._complete.is_set():
            # Some 'data'
            self._cluster.add_objects(0, random.randint(10, 20), 1024 * 1024 * 4)
            # Some 'metadata'
            self._cluster.add_objects(1, random.randint(10, 20), 1024)

            self._complete.wait(interval)

    def stop(self):
        self._complete.set()