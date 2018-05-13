# -*- coding: utf-8 -*-

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class TimeoutError(Exception):
    pass


class Messager(object):
    """A typed messager.

    Keyword Arguments:
        queue_cls (Queue): A queue class.

        size (int or None): The argument of ``queue_cls``.
    """

    def __init__(self, queue_cls=Queue, size=None):
        self._queue = queue_cls(size)

    def send(self, type, data=None, timeout=None):
        """Send a type ``type`` message with the data ``data``.

        Args:
            type (object): The message type.

        Keyword Arguments:
            data (object): The message data.

            timeout (number or None): If ``None``, it will block until sending
                the message successfully. If a positive number, it will block
                at most ``timeout`` seconds or raise the ``TimeoutError``
                exception if failed to send the message within that time.
        """

        try:
            self._queue.put((type, data), timeout=timeout)
        except Exception:
            raise TimeoutError

    def recv(self, timeout=None):
        """Receive an typed message.

        Keyword Arguments:
            timeout (number or None): If ``None``, it will block until receiving
                a message successfully. If a positive number, it will block
                at most ``timeout`` seconds or raise the ``TimeoutError``
                exception if failed to receive a message within that time.

        Returns:
             tuple: A 2-member tuple consisting of a type and a data.
        """

        try:
            data = self._queue.get(timeout=timeout)
            self._queue.task_done()
            return data
        except Exception:
            raise TimeoutError

    def __iter__(self):
        return self

    def __next__(self):
        return self.recv()

    # For Python 2
    def next(self):
        return self.__next__()
