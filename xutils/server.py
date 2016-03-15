# encoding: utf-8
from __future__ import absolute_import, print_function, unicode_literals
import os
import socket
import logging
import functools
import traceback

import greenlet
import eventlet

from oslo_service import service, wsgi

LOG = logging.getLogger(__name__)


def listen_socket(host, port, backlog=1024, reuse=True):
    sock = socket.socket()
    if reuse:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(backlog)
    return sock


def wrap_exc(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            return None
    return inner


def BaseRequestHandlerWrapper(HandlerClass):
    """A wrapper or adapter of BaseRequestHandler.

    By this, you can use BaseRequestHandler, StreamRequestHandler,
    DatagramRequestHandler of SocketServer in Python 2, or of socketserver in
    Python 3.
    """
    def wrapper(conn, addr):
        return HandlerClass(conn, addr, None)

    return wrapper


class HandlerBase(object):
    def __call__(self, client_sock, client_addr):
        raise NotImplementedError("__call__ MUST be implemented")


class ServerBase(service.ServiceBase):
    def __init__(self, pool_size=10240):
        self.pool_size = pool_size
        self._pool = eventlet.GreenPool(self.pool_size)
        self._server = None

    def serve(self, pool):
        raise NotImplementedError("The method of serve MUST be implemented")

    def _spawn(self, pool):
        pid = os.getpid()
        try:
            self.serve(pool)
        finally:
            pool.waitall()
            LOG.info("[Process{0}] the server exited".format(pid))

    def start(self):
        self._server = eventlet.spawn(self.serve, pool=self._pool)

    def stop(self):
        if self._server is not None:
            # let eventlet close socket
            self._pool.resize(0)
            self._server.kill()

    def wait(self):
        try:
            if self._server is not None:
                num = self._pool.running()
                LOG.debug("Waiting server to finish %d requests.", num)
                self._pool.waitall()
        except greenlet.GreenletExit:
            LOG.info("Server has stopped.")

    def reset(self):
        self._pool.resize(self.pool_size)


class TCPServer(ServerBase):
    def __init__(self, handler, host, port, pool_size=10240, backlog=1024, timeout=None):
        self.host = host
        self.port = port
        self.sock = listen_socket(self.host, self.port, backlog)
        LOG.info("Listen %s:%s" % (self.host, self.port))
        self.handler = handler
        self.timeout = timeout
        super(TCPServer, self).__init__(pool_size)

    def handle(self, conn, addr):
        try:
            self.handler(conn, addr)
        except socket.timeout:
            LOG.info("socket from {0} time out".format(addr))
        finally:
            try:
                conn.close()
            except socket.error:
                pass

    def serve(self, pool):
        pid = os.getpid()
        try:
            while True:
                try:
                    conn, addr = self.sock.accept()
                    conn.settimeout(self.timeout)
                    LOG.debug("[Process{0}] accepted {1}".format(pid, addr))
                    pool.spawn_n(self.handle, conn, addr)
                except socket.error as e:
                    LOG.error("[Process{0}] Socket has a error {1}: {2}".format(pid, addr, e))
                except Exception as e:
                    LOG.error(traceback.format_exc())
                    LOG.error("[Process{0}] can not handle the request from {1}: {2}".format(pid, addr, e))
                except (KeyboardInterrupt, SystemExit):
                    LOG.info("[Process{0}] the server is exiting".format(pid))
                    break
        finally:
            try:
                self.sock.close()
            except socket.error as e:
                pass
SocketServer = TCPServer


class TaskServer(ServerBase):
    EXTRA_TASH_NUM = 3

    def __init__(self, task_fn, *args, **kwargs):
        self.task_fn = task_fn
        self.task_num = kwargs.pop("task_num", 1)
        self.args = args
        self.kwargs = kwargs
        super(TaskServer, self).__init__(self.task_num + self.EXTRA_TASH_NUM)

    def _wrap_exc(self):
        try:
            self.task_fn(*self.args, **self.kwargs)
        except Exception:
            LOG.error(traceback.format_exc())

    def serve(self, pool):
        for i in range(self.task_num):
            pool.spawn_n(self._wrap_exc)
        LOG.info("Process{0} start {1} tasks".format(os.getpid(), self.task_num))


class PoolServer(ServerBase):
    def __init__(self, handler, *args, **kwargs):
        pool_size = kwargs.pop("pool_size", 10240)
        self.handler = handler
        self.args = args
        self.kwargs = kwargs
        super(PoolServer, self).__init__(pool_size)

    def serve(self, pool):
        try:
            self.handler(pool, *self.args, **self.kwargs)
        except Exception:
            LOG.error(traceback.format_exc())


# Below the version of 0.10.0, oslo_service.wsgi.Server doesn't inherit
# oslo_service.wsgi.ServiceBase. So, if using the version below 0.10.0,
# you SHOULD inherit oslo_service.wsgi.ServiceBase.
class WSGIServer(wsgi.Server):
    def __init__(self, *args, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", 10240)
        super(WSGIServer, self).__init__(*args, **kwargs)
