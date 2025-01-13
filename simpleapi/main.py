from simpleapi.request import Request
from simpleapi.response import Response
from parse import parse
from typing import Any
import types


class SimpleAPI:
    """SimpleAPI class to create a simple API"""

    def __init__(self, middlewares=[]) -> None:
        self.routes = dict()
        self.middlewares = middlewares
        self.middlewares_for_routes = dict()

    def __call__(self, environ, start_response) -> Any:
        response = Response()
        request = Request(environ)

        for middleware in self.middlewares:
            if isinstance(middleware, types.FunctionType):
                middleware(request)
            else:
                raise TypeError("Middleware must be a function")

        for path, handler_dict in self.routes.items():
            res = parse(path, request.path_info)
            for request_method, handler in handler_dict.items():
                if request.request_method == request_method and res:

                    route_mw_list = self.middlewares_for_routes[path][request_method]
                    for route_mw in route_mw_list:
                        if isinstance(route_mw, types.FunctionType):
                            route_mw(request)
                        else:
                            raise TypeError("Middleware must be a function")

                    handler(request, response, **res.named)
                    return response.as_wsgi(start_response)

        return response.as_wsgi(start_response)

    def common_route(self, path, request_method, handler, middlewares):
        """Common function to add a route to the API"""

        """Add routes to the Routes dictionary"""
        path_name = path or f"/{handler.__name__}"

        if path_name not in self.routes:
            self.routes[path_name] = {}

        self.routes[path_name][request_method] = handler

        """Add middlewares to the middlewares_for_routes dictionary"""

        if path_name not in self.middlewares_for_routes:
            self.middlewares_for_routes[path_name] = {}
        self.middlewares_for_routes[path_name][request_method] = middlewares

        return handler

    def get(self, path=None, middlewares=[]):
        """Decorator to add a GET route to the API"""

        def wrapper(handler):
            return self.common_route(path, "GET", handler, middlewares)

        return wrapper

    def post(self, path=None):
        """Decorator to add a POST route to the API"""

        def wrapper(handler):
            return self.common_route(path, "POST", handler)

        return wrapper

    def put(self, path=None):
        """Decorator to add a PUT route to the API"""

        def wrapper(handler):
            return self.common_route(path, "PUT", handler)

        return wrapper

    def delete(self, path=None):
        """Decorator to add a DELETE route to the API"""

        def wrapper(handler):
            return self.common_route(path, "DELETE", handler)

        return wrapper
