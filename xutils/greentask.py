# encoding: utf-8
from __future__ import absolute_import, print_function, unicode_literals, division

try:
    import eventlet
    eventlet.monkey_patch(all=True)
except ImportError:
    from threading import Thread
    eventlet = None


def spawn_task(task_f, *args, **kwargs):
    if eventlet:
        eventlet.spawn_n(task_f, *args, **kwargs)
    else:
        t = Thread(target=task_f, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
