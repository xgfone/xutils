# encoding: utf8
from __future__ import print_function, unicode_literals, absolute_import

import redis


class FILOQueue(object):
    def __init__(self, conn=None, queue="default_queue"):
        """Initial the queue.

        :param conn: A dict or instance of redis.Redis. If a dict, it'll connect
                    to the redis server with it.
        :param queue: A str representing the queue name.
        """
        self.default_queue = queue
        if conn is None:
            kwargs = {
                "host": "localhost",
                "port": 6379,
                "db": 0,
            }
            self.redis = redis.Redis(**kwargs)
        elif isinstance(conn, (redis.Redis, redis.StrictRedis)):
            self.redis = redis
        else:
            self.redis = redis.Redis(**conn)

    def queue(self, queue=None):
        queue = queue if queue else self.default_queue
        if not queue:
            raise ValueError("No assign a queue name")
        return queue

    def push(self, queue=None, *datas):
        """Push the datas into the FILO queue."""
        queue = self.queue(queue)
        return self.redis.lpush(queue, *datas)

    def pop(self, queue=None, timeout=0):
        """Pop the value from the FILO queue `queue`.

        :param queue(str): the queue name, not a list of str.
        :param timeout(int): the timeout. If 0, block indefinitely.
        """
        queue = self.queue(queue)
        return self.redis.brpop(queue, timeout=timeout)[1]
