import time
import logging

from multiprocessing import Process
from threading import Lock

LOG = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self):
        self._tasks = {}
        self._lock = Lock()
        self._quit = False

    def _spawn_task(self, task):
        worker = Process(target=task[0], args=task[1], kwargs=task[2])
        worker.daemon = True
        worker.start()
        return worker

    def launch_task(self, func, *args, **kwargs):
        workers = kwargs.pop("workers", 1)
        if workers < 1:
            raise ValueError("workers is less than 1")

        task = func, args, kwargs
        while workers > 0:
            workers -= 1
            worker = self._spawn_task(task)
            self._tasks[worker] = task

    def quit(self):
        with self._lock:
            self._quit = True

    def wait(self, reload=True):
        while True:
            time.sleep(1)

            with self._lock:
                if self._quit:
                    for worker in self._tasks:
                        worker.terminate()
                    return

            try:
                self._wait(reload)
            except Exception as err:
                LOG.error(err)
                return

    def _wait(self, reload):
        removes = []
        adds = []
        for worker, task in self._tasks.items():
            if not worker.is_alive():
                LOG.warning("Process[%d] exited", worker.pid)
                removes.append(worker)
                if reload:
                    worker = self._spawn_task(task)
                    adds.append((worker, task))

        for worker in removes:
            self._tasks.pop(worker, None)

        for worker, task in adds:
            self._tasks[worker] = task
            LOG.warning("Reload the task on Process[%d]: func=%s, args=%s, kwargs=%s",
                        worker.pid, task[0], task[1], task[2])
