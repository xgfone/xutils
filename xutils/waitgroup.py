import threading as _threading


class WaitGroup(object):
    def __init__(self):
        self._cond = _threading.Condition()
        self._lock = _threading.Lock()
        self._num = 0

    def add(self, num=1):
        with self._lock:
            if self._num < 0:
                raise RuntimeError("the WaitGroup has been over")
            self._num += num

    def done(self):
        with self._lock:
            self._num -= 1
            if self._num < 0:
                raise RuntimeError("call done() too many")
            notice = self._num == 0

        if notice:
            with self._cond:
                self._cond.notify_all()

    def wait(self, timeout=None):
        with self._cond:
            self._cond.wait(timeout=timeout)
