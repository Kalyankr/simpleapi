from simpleapi.request import Request
from simpleapi.response import Response
from parse import parse
from typing import Any, Callable, Dict, List
import types
import sys


class SimpleAPI:
    """SimpleAPI class to create a simple API"""

    def __init__(self, middlewares: List[Callable] = None) -> None:
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middlewares = middlewares or []
        self.middlewares_for_routes: Dict[str, Dict[str, List[Callable]]] = {}

    def __call__(self, environ, start_response) -> Any:
        response = Response()
        request = Request(environ)

        try:
            # Apply global middlewares
            for middleware in self.middlewares:
                if isinstance(middleware, types.FunctionType):
                    middleware(request)
                else:
                    raise TypeError("Global middleware must be a function")

            # Match routes and handlers
            for path, handler_dict in self.routes.items():
                res = parse(path, request.path_info)
                if res:
                    for request_method, handler in handler_dict.items():
                        if request.request_method == request_method:
                            # Apply route-specific middlewares
                            route_mw_list = self.middlewares_for_routes.get(
                                path, {}
                            ).get(request_method, [])
                            for route_mw in route_mw_list:
                                if isinstance(route_mw, types.FunctionType):
                                    route_mw(request, response)
                                else:
                                    raise TypeError(
                                        "Route middleware must be a function"
                                    )

                            # Call the route handler
                            handler(request, response, **res.named)
                            return response.as_wsgi(start_response)
            # If no route matches
            response.status_code = 404
            response.body = b"Route not found"
        except Exception as e:
            # Handle exceptions and return error response
            response.status_code = 500
            response.body = str(e).encode("utf-8")
            print(e)

        return response.as_wsgi(start_response)

    def common_route(
        self,
        path: str,
        request_method: str,
        handler: Callable,
        middlewares: List[Callable],
    ) -> Callable:
        """Common function to add a route to the API"""
        path_name = path or f"/{handler.__name__}"

        # Add the route to the routes dictionary
        self.routes.setdefault(path_name, {})[request_method] = handler

        # Add middlewares for the route
        self.middlewares_for_routes.setdefault(path_name, {})[
            request_method
        ] = middlewares

        return handler

    def get(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a GET route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "GET", handler, middlewares)

        return wrapper

    def post(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a POST route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "POST", handler, middlewares)

        return wrapper

    def put(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a PUT route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "PUT", handler, middlewares)

        return wrapper

    def delete(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a DELETE route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "DELETE", handler, middlewares)

        return wrapper

    def run(self, host=None, port=None, debug=None):
        """Run the app using Gunicorn."""
        import os
        import subprocess

        host = host or os.getenv("SIMPLEAPI_HOST", "127.0.0.1")
        port = port or os.getenv("SIMPLEAPI_PORT", "8000")
        debug = (
            debug
            if debug is not None
            else os.getenv("SIMPLEAPI_DEBUG", "False") == "True"
        )

        app_file = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        command = [
            "gunicorn",
            f"{app_file}:app",
            "--bind",
            f"{host}:{port}",
        ]
        if debug:
            command.append("--reload")
        subprocess.run(command)
