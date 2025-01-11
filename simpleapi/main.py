from simpleapi.request import Request
from simpleapi.response import Response
from parse import parse
from typing import Any
import types


class SimpleAPI:

    def __init__(self, middlewares=[]) -> None:
        self.routes = dict()
        self.middlewares = middlewares
        self.middlewares_for_routes = dict()

    def __call__(self, environ, start_response) -> Any:
        response = Response()
        request = Request(environ)

        for path, handler_dict in self.routes.items():
            print(path)
            res = parse(path, request.path_info)
            for request_method, handler in handler_dict.items():
                if request.request_method == request_method and res:
                    print(f"these are values {res.named}")
                    handler(request, response, **res.named)
                    return response.as_wsgi(start_response)

        return response.as_wsgi(start_response)

    def get(self, path=None):

        def wrapper(handler):

            path_name = path or f"/{handler.__name__}"
            if path_name not in self.routes:
                self.routes[path_name] = {}

            self.routes[path_name]["GET"] = handler

            return handler

        return wrapper
