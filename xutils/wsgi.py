
# -*- coding: utf-8 -*-

import sys
import json
import logging
import traceback

import falcon
import xutils

from wsgiref.simple_server import WSGIRequestHandler, WSGIServer as _WSGIServer
try:
    from socketserver import ThreadingMixIn
except ImportError:
    from SocketServer import ThreadingMixIn

LOG = logging.getLogger("gunicorn.error" if "gunicorn" in sys.modules else __name__)

STATUS_CODES = {}
for v in vars(falcon.status_codes).values():
    if xutils.is_string(v):
        try:
            code = int(v.split(maxsplit=1)[0])
            STATUS_CODES[code] = v
        except Exception:
            pass


class WSGIServer(ThreadingMixIn, _WSGIServer):
    daemon_threads = True       # The entire program exits when the main thread left.
    timeout = 30                # Wait until a request arrives or the timeout expires
    request_queue_size = 128    # The bocklog size of the listening socket
    allow_reuse_address = True  # Reuse the address listened to

    def __init__(self, addr, application, RequestHandlerClass=WSGIRequestHandler,
                 bind_and_activate=True):
        super(WSGIServer, self).__init__(addr, RequestHandlerClass, bind_and_activate)
        self.set_app(application)


class Resource(object):
    def status(self, status):
        if isinstance(status, int):
            return STATUS_CODES[status]
        return status

    def load_json(self, req):
        data = req.bounded_stream.read()
        return json.loads(data) if data else None

    def dump_json(self, resp, result, status=None, separators=(',', ':')):
        resp.body = json.dumps(result, separators=separators)
        resp.content_type = falcon.MEDIA_JSON
        resp.status = self.status(status or falcon.HTTP_200)


class Application(falcon.API):
    def append_error_handler(self, exception, handler=None):
        self._error_handlers.append((exception, handler or exception.handle))

    def traceback_exception(self, ex, req, resp, params):
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_500
        resp.body = str(ex)
        LOG.error("Get an exception: method=%s, url=%s, err=%s",
                  req.method, req.path, ex)
        LOG.error(traceback.format_exc())

    def _get_action(self, resource, action):
        return action if callable(action) else getattr(resource, action)

    def map_http_methods(self, resource, args, kwargs):
        """Map the HTTP methods.

        Support:
            >>> add_route("/path/to", resource) # The origin
            >>> add_route("/path/to", resource, map={"GET": "resource_method"})
            >>> add_route("/path/to", resource, map={"GET": resource.method})
            >>> add_route("/path/to", resource, get="resource_method")
            >>> add_route("/path/to", resource, get=resource.method)

        For Example:
            >>> class Resource(object):
            >>>     def on_get(self, req, resp, name):
            >>>         resp.body = name
            >>>
            >>> resource = Resource()
            >>> add_route("/v1/hello/{name}", resource)
            >>> add_route("/v2/hello/{name}", resource, map={"GET": "on_get"})
            >>> add_route("/v3/hello/{name}", resource, map={"GET": resource.on_get})
            >>> add_route("/v3/hello/{name}", resource, get="on_get")
            >>> add_route("/v3/hello/{name}", resource, get=resource.on_get)
        """

        m = kwargs.pop("map", None)
        if m:
            return {k.upper(): self._get_action(resource, v) for k, v in m.items()}

        mmap = {}
        for method in tuple(kwargs.keys()):
            _method = method.upper()
            if _method in falcon.COMBINED_METHODS:
                mmap[_method] = self._get_action(resource, kwargs.pop(method))

        return mmap if mmap else falcon.routing.map_http_methods(resource)

    def add_route(self, uri_template, resource, *args, **kwargs):
        if not uri_template.startswith('/'):
            raise ValueError("uri_template must start with '/'")

        if '//' in uri_template:
            raise ValueError("uri_template may not contain '//'")

        args = list(args)
        method_map = self.map_http_methods(resource, args, kwargs)
        falcon.routing.set_default_responders(method_map)
        self._router.add_route(uri_template, method_map, resource, *args, **kwargs)


if __name__ == "__main__":

    class _Resource(object):
        def on_get(self, req, resp, name):
            resp.body = name

    application = Application()
    resource = _Resource()
    application.add_route("/v1/hello/{name}", resource)
    application.add_route("/v2/hello/{name}", resource, map={"GET": "on_get"})
    application.add_route("/v3/hello/{name}", resource, map={"GET": resource.on_get})
    application.add_route("/v4/hello/{name}", resource, get="on_get")
    application.add_route("/v5/hello/{name}", resource, get=resource.on_get)

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    with WSGIServer(("", port), application) as httpd:
        print("WSGI server listening on %s" % port)
        httpd.serve_forever()
