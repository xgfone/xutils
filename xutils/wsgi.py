
# -*- coding: utf-8 -*-

import sys
import json
import logging
import traceback

import falcon
import xutils

LOG = logging.getLogger("gunicorn.error" if "gunicorn" in sys.modules else __name__)

STATUS_CODES = {}
for v in vars(falcon.status_codes).values():
    if xutils.is_string(v):
        try:
            code = int(v.split(maxsplit=1)[0])
            STATUS_CODES[code] = v
        except Exception:
            pass


class Application(falcon.API):
    def to_status(self, status):
        if isinstance(status, int):
            return STATUS_CODES[status]
        return status

    def json(self, req, resp, result, status=None, separators=(',', ':')):
        resp.body = json.dumps(result, separators=separators)
        resp.content_type = falcon.MEDIA_JSON
        resp.status = self.to_status(status or falcon.HTTP_200)

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
            ### The Old API
            >>> add_route("/path/to", resource)

            ### New API
            >>> add_route("/path/to", resource, "resource_method")  # Default GET
            >>> add_route("/path/to", resource, "resource_method", "GET")
            >>> add_route("/path/to", resource, "resource_method", "GET", "POST")
            >>> add_route("/path/to", resource, "resource_method", ["GET", "POST"])
            >>>
            >>> add_route("/path/to", resource, callable_action)  # Default GET
            >>> add_route("/path/to", resource, callable_action, "GET")
            >>> add_route("/path/to", resource, callable_action, "GET", "POST")
            >>> add_route("/path/to", resource, callable_action, ["GET", "POST"])
            >>>
            >>> add_route("/path/to", resource, "resource_method", methods="GET")
            >>> add_route("/path/to", resource, "resource_method", methods=["GET"])
            >>>
            >>> add_route("/path/to", resource, callable_action, methods="GET")
            >>> add_route("/path/to", resource, callable_action, methods=["GET"])
            >>>
            >>> add_route("/path/to", resource, action="resource_method", methods="GET")
            >>> add_route("/path/to", resource, action="resource_method", methods=["GET"])
            >>>
            >>> add_route("/path/to", resource, action=callable_action, methods="GET")
            >>> add_route("/path/to", resource, action=callable_action, methods=["GET"])

        For Example:
            >>> class Resource(object):
            >>>     def hello(self, req, resp, name):
            >>>         resp.body = name
            >>>
            >>> resource = Resource()
            >>> add_route("/v1/hello/{name}", resource, "hello")
            >>> add_route("/v2/hello/{name}", resource, resource.hello)
            >>> add_route("/v3/hello/{name}", resource, resource.hello, "GET")
        """

        if not args and not kwargs:
            return falcon.routing.map_http_methods(resource)

        _map = kwargs.get("map", None)
        if _map:
            return {k: self._get_action(resource, v) for k, v in _map.items()}

        if args:
            action = args[0]
            methods = args[1:]
            if not methods:
                methods = kwargs.pop("methods", None)
        else:
            action = kwargs.pop("action", None)
            methods = kwargs.pop("methods", None)

        if not action:
            raise ValueError("no action")

        action = self._get_action(resource, action)
        if not methods:
            methods = ["GET"]
        if not isinstance(methods, (list, tuple)):
            methods = [methods]

        args.clear()
        kwargs.pop("action", None)
        kwargs.pop("methods", None)
        return {method.upper(): action for method in methods}

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
    from wsgiref.simple_server import make_server, WSGIServer as _WSGIServer

    try:
        from socketserver import ThreadingMixIn
    except ImportError:
        from SocketServer import ThreadingMixIn

    class WSGIServer(ThreadingMixIn, _WSGIServer):
        daemon_threads = True

    class Resource(object):
        def hello(self, req, resp, name):
            resp.body = name

    application = Application()
    resource = Resource()
    application.add_route("/v1/hello/{name}", resource, "hello")
    application.add_route("/v2/hello/{name}", resource, resource.hello)
    application.add_route("/v3/hello/{name}", resource, resource.hello, "GET")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    with make_server("", port, application, WSGIServer) as httpd:
        print("WSGI server listening on %s" % port)
        httpd.serve_forever()
