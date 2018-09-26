# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import eventlet
from gunicorn.workers.geventlet import EventletWorker


class EventletTaskWorker(EventletWorker):
    """The task worker based on eventlet.

    Notice: the application is not WSGI application, which only receives
    one argument, the eventlet green pool.
    """

    def init_process(self):
        self.patch()
        super(EventletTaskWorker, self).init_process()

    def run_as_task(self, concurrency):
        pool = eventlet.GreenPool(concurrency)
        try:
            self.app.wsgi()(pool)
        except eventlet.StopServe:
            pool.waitall()

    def run(self):
        for sock in self.sockets:
            sock.close()
        task_func = eventlet.spawn(self.run_as_task, self.worker_connections)

        while self.alive:
            self.notify()
            eventlet.sleep(1.0)

        self.notify()
        try:
            with eventlet.Timeout(self.cfg.graceful_timeout) as t:
                task_func.kill(eventlet.StopServe())
                task_func.wait()
        except eventlet.Timeout as te:
            if te != t:
                raise
            task_func.kill()
