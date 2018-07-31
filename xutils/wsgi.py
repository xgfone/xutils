
# -*- coding: utf-8 -*-

import sys
import json
import logging
import traceback

import falcon
import xutils

from xutils.util import json_loads
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer as _WSGIServer
try:
    from socketserver import ThreadingMixIn
except ImportError:
    from SocketServer import ThreadingMixIn

LOG = logging.getLogger("gunicorn.error" if "gunicorn" in sys.modules else __name__)

Application = API = falcon.API
STATUS_CODES = {}
for v in vars(falcon.status_codes).values():
    if xutils.is_string(v):
        try:
            code = int(v.split()[0])
            STATUS_CODES[code] = v
        except Exception:
            pass


class WSGIServer(ThreadingMixIn, _WSGIServer, object):
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

    def respond(self, resp, status=None, body=None, content_type=None):
        resp.status = self.status(status or falcon.HTTP_200)
        if content_type:
            resp.content_type = content_type
        if body:
            resp.body = body

    def dump_json(self, resp, result, status=None, separators=(',', ':')):
        body = json.dumps(result, separators=separators)
        self.respond(resp, status, body, falcon.MEDIA_JSON)

    def load_json(self, req, data=None):
        data = data or req.bounded_stream.read()
        return json_loads(data) if data else None


class Router(falcon.routing.DefaultRouter):
    def _get_action(self, resource, action):
        return action if callable(action) else getattr(resource, action)

    def map_http_methods(self, resource, **kwargs):
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

        return mmap if mmap else self.map_http_methods(resource, **kwargs)


def append_error_handler(app, exception, handler=None):
    app._error_handlers.append((exception, handler or exception.handle))


def get_exception_handler(get_body=None, traceback_exception=False):
    """Return an exception handler of falcon.

    Keyword Arguments:
        get_body (function): a function to return a response body.
            Its arguments are the same of the exception handler of falcon,
            that's, ``get_body(ex, req, resp, params)``. Its return value
            will be assigned to ``resp.body``.
    """

    def _traceback_exception(ex, req, resp, params):
        resp.content_type = falcon.MEDIA_TEXT
        resp.status = falcon.HTTP_500
        resp.body = get_body(ex, req, resp, params) if callable(get_body) else str(ex)
        LOG.error("Get an exception: method=%s, url=%s, err=%s", req.method, req.uri, ex)
        if traceback_exception:
            LOG.error(traceback.format_exc())

    return _traceback_exception


def _add_route(self, uri_template, resource, *args, **kwargs):
    if not xutils.is_string(uri_template):
        raise TypeError('uri_template is not a string')

    if not uri_template.startswith('/'):
        raise ValueError("uri_template must start with '/'")

    if '//' in uri_template:
        raise ValueError("uri_template may not contain '//'")

    if kwargs and hasattr(self._router, "map_http_methods"):
        method_map = self._router.map_http_methods(resource, **kwargs)
    else:
        method_map = falcon.routing.map_http_methods(resource)
    falcon.routing.set_default_responders(method_map)
    self._router.add_route(uri_template, method_map, resource)
falcon.API.add_route = _add_route


if __name__ == "__main__":

    class _Resource(object):
        def on_get(self, req, resp, name):
            resp.body = name

    resource = _Resource()
    app = falcon.API(router=Router())
    append_error_handler(app, Exception, get_exception_handler())
    app.add_route("/v1/hello/{name}", resource)
    app.add_route("/v2/hello/{name}", resource, map={"GET": "on_get"})
    app.add_route("/v3/hello/{name}", resource, map={"GET": resource.on_get})
    app.add_route("/v4/hello/{name}", resource, get="on_get")
    app.add_route("/v5/hello/{name}", resource, get=resource.on_get)

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    with WSGIServer(("", port), app) as httpd:
        print("WSGI server listening on %s" % port)
        httpd.serve_forever()
