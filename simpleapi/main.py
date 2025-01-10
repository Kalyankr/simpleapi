from tracemalloc import start
import json


class SimpleAPI:

    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):

        for route, handler_dict in self.routes.items():
            for method, handler in handler_dict.items():
                if (
                    environ["PATH_INFO"] == route
                    and environ["REQUEST_METHOD"] == method
                ):
                    start_response("200 OK", [("Content-Type", "text/plain")])
                    result = handler()

                    return [result.encode("utf-8")]

    def get(self, route):

        def wrapper(handler):
            path_info = route or f"/{handler.__name__}"
            if path_info not in self.routes:
                self.routes[path_info] = {}
            self.routes[path_info]["GET"] = handler

            return handler

        return wrapper
