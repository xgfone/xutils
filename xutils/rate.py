# -*- coding: utf-8 -*-

from __future__ import division

import time

from threading import Thread
try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class Rate(object):
    def __init__(self, rate, hz=10):
        if rate < 1 or hz < 1:
            raise ValueError("rate and hz must be a positive integer")

        _rate = rate // hz
        _rate, interval = (_rate, 1.0 / hz) if _rate else (1, 1.0 / rate)

        self._rate = _rate
        self._interval = interval
        self._queue = Queue(rate)

        self._thread = Thread(target=self._start)
        self._thread.daemon = True
        self._thread.start()

    def _start(self):
        while True:
            diff = self._rate - self._queue.qsize()
            while diff > 0:
                self._queue.put(None)
                diff -= 1
            time.sleep(self._interval)

    def get_token(self):
        """Return a token if exists. Or it will be blocked."""

        self._queue.get()
        self._queue.task_done()

    def allow(self):
        """Return True if there is a token, or False. It never be blocked."""

        try:
            self._queue.get_nowait()
        except Exception:
            return False
        else:
            return True
