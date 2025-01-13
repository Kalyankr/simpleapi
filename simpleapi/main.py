import subprocess
import sys
import os
import types
import logging
import inspect
import json
from typing import Any, Callable, Dict, List, Optional
from parse import parse
from simpleapi.request import Request
from simpleapi.response import Response

# Set up the logger
logging.basicConfig(
    level=logging.DEBUG,  # You can set this to INFO, ERROR, etc.
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class SimpleAPI:
    """SimpleAPI class to create a simple API"""

    def __init__(self, middlewares: List[Callable] = None) -> None:
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middlewares = middlewares or []
        self.middlewares_for_routes: Dict[str, Dict[str, List[Callable]]] = {}
        self.openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "SimpleAPI",
                "version": "1.0.0",
                "description": "A dynamic API with Swagger/OpenAPI documentation",
            },
            "paths": {},
        }
        self.get("/openapi.json")(self._serve_openapi_spec)

        # Log the initialization of the app
        logger.info("SimpleAPI initialized.")

    def _validate_middleware(self, middleware: Callable) -> None:
        """Validate that a middleware is a callable function."""
        if not isinstance(middleware, types.FunctionType):
            logger.error("Middleware is not callable: %s", middleware)
            raise TypeError("Middleware must be a function")

    def __call__(self, environ, start_response) -> Any:
        response = Response()
        request = Request(environ)

        try:
            # Log incoming request
            logger.info(
                "Incoming request: %s %s", request.request_method, request.path_info
            )

            # Apply global middlewares
            for middleware in self.middlewares:
                self._validate_middleware(middleware)
                middleware(request, response)

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
                                self._validate_middleware(route_mw)
                                route_mw(request, response)

                            # Call the route handler
                            logger.info("Matched route: %s %s", request_method, path)
                            handler(request, response, **res.named)
                            return response.as_wsgi(start_response)

            # If no route matches
            response.status_code = 404
            response.body = b"Route not found"
            logger.warning("Route not found: %s", request.path_info)

        except Exception as e:
            # Handle exceptions and return error response
            response.status_code = 500
            response.body = str(e).encode("utf-8")
            logger.error("Error processing request: %s", str(e), exc_info=True)

        return response.as_wsgi(start_response)

    def common_route(
        self,
        path: str,
        request_method: str,
        handler: Callable,
        middlewares: List[Callable],
        doc: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """Common function to add a route to the API"""
        path_name = path or f"/{handler.__name__}"

        # Add the route to the routes dictionary
        self.routes.setdefault(path_name, {})[request_method] = handler

        # Automatically generate OpenAPI documentation
        if not doc:
            doc = self.generate_route_doc(handler)

        # Add the route documentation to the OpenAPI spec
        self.openapi_spec["paths"].setdefault(path_name, {})[request_method] = doc

        # Add middlewares for the route
        self.middlewares_for_routes.setdefault(path_name, {})[
            request_method
        ] = middlewares

        logger.info("Route added: %s %s", request_method, path_name)

        return handler

    def generate_route_doc(self, handler: Callable) -> Dict[str, Any]:
        """Generate documentation for a route dynamically"""
        doc = {
            "summary": handler.__name__,
            "description": f"Handler for {handler.__name__}",
            "parameters": self.get_parameters_from_signature(handler),
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {"example": {}}  # Example response body
                    },
                },
                "404": {"description": "Not Found"},
                "500": {"description": "Internal Server Error"},
            },
        }
        return doc

    def get_parameters_from_signature(self, handler: Callable) -> List[Dict[str, Any]]:
        """Extract parameters from function signature for documentation"""
        params = []
        signature = inspect.signature(handler)
        for param in signature.parameters.values():
            # Skip request and response parameters
            if param.name in ["request", "response"]:
                continue

            param_doc = {
                "name": param.name,
                "in": "query" if param.annotation == Request else "body",
                "required": param.default == inspect.Parameter.empty,
            }
            params.append(param_doc)
        return params

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

    def patch(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a PATCH route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "PATCH", handler, middlewares)

        return wrapper

    def head(self, path: str = None, middlewares: List[Callable] = None):
        """Decorator to add a HEAD route to the API"""
        middlewares = middlewares or []

        def wrapper(handler: Callable):
            return self.common_route(path, "HEAD", handler, middlewares)

        return wrapper

    def run(self, host=None, port=None, debug=None, use_gunicorn=True):
        """Run the app with an option to use Gunicorn or a custom server."""
        host = host or os.getenv("SIMPLEAPI_HOST", "127.0.0.1")
        port = port or os.getenv("SIMPLEAPI_PORT", "8000")
        debug = (
            debug
            if debug is not None
            else os.getenv("SIMPLEAPI_DEBUG", "False") == "True"
        )

        logger.info("Running SimpleAPI on %s:%s", host, port)

        if use_gunicorn:
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
        else:
            # Optionally add custom WSGI server here
            pass

    def get_openapi_spec(self) -> str:
        """Return the OpenAPI specification as a JSON response."""
        return json.dumps(self.openapi_spec, indent=2)

    def _serve_openapi_spec(self, request, response):
        """Serve the OpenAPI specification."""
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response.body = self.get_openapi_spec().encode("utf-8")
