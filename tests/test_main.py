import pytest
from simpleapi_kkr import SimpleAPI
from simpleapi_kkr.request import Request
from simpleapi_kkr.response import Response


# Mock middlewares and handlers for tests
def mock_middleware(request, response):
    response.body += b" Middleware Applied"


def mock_handler(request, response, **kwargs):
    response.body = b"Hello, World!"


@pytest.fixture
def api():
    # Initialize the SimpleAPI instance
    return SimpleAPI()


def test_route_registration(api):
    # Define a mock handler for GET requests
    @api.get("/test")
    def test_handler(request, response):
        response.status_code = 200
        response.body = b"Test Route"

    # Simulate a request
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/test"}
    start_response = lambda status, headers: None

    # Call the API's `__call__` method (to simulate a request)
    result = api.__call__(environ, start_response)

    # The result of `__call__` is the response body as bytes
    response_body = b"".join(result)

    # Check that the response body matches the expected result
    assert response_body == b"Test Route"
    assert result.status_code == 200


def test_middleware_execution(api):
    # Define a mock handler for GET requests
    @api.get("/middleware")
    def middleware_handler(request, response):
        response.body = b"Handler Executed"

    # Simulate a request
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/middleware"}
    start_response = lambda status, headers: None
    request = Request(environ)
    response = Response()

    # Apply a mock middleware that modifies the response body
    api.middlewares.append(mock_middleware)

    # Call the API's `__call__` method (to simulate a request)
    api.__call__(environ, start_response)

    # Check that the middleware has been executed
    assert b"Middleware Applied" in response.body
    assert b"Handler Executed" in response.body
    assert response.status_code == 200


def test_serve_openapi_spec(api):
    # Check that the OpenAPI spec can be served
    @api.get("/openapi.json")
    def openapi_handler(request, response):
        response.body = api.get_openapi_spec().encode("utf-8")

    # Simulate a request for the OpenAPI spec
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/openapi.json"}
    start_response = lambda status, headers: None
    request = Request(environ)
    response = Response()

    # Call the API's `__call__` method (to simulate a request)
    api.__call__(environ, start_response)

    # Check if the response contains OpenAPI spec JSON
    assert response.status_code == 200
    assert b"openapi" in response.body
    assert b"title" in response.body
    assert b"version" in response.body


def test_route_not_found(api):
    # Simulate a request to a non-existent route
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/nonexistent"}
    start_response = lambda status, headers: None
    request = Request(environ)
    response = Response()

    # Call the API's `__call__` method (to simulate a request)
    api.__call__(environ, start_response)

    # Check that the response status code is 404
    assert response.status_code == 404
    assert response.body == b"Route not found"


def test_route_with_parameters(api):
    # Define a mock handler for GET requests with a path parameter
    @api.get("/hello/{name}")
    def hello_handler(request, response, name):
        response.body = f"Hello, {name}!".encode("utf-8")

    # Simulate a request with a path parameter
    environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/hello/world"}
    start_response = lambda status, headers: None
    request = Request(environ)
    response = Response()

    # Call the API's `__call__` method (to simulate a request)
    api.__call__(environ, start_response)

    # Check that the response body contains the dynamic name
    assert response.body == b"Hello, world!"
    assert response.status_code == 200


def test_route_with_invalid_method(api):
    # Define a mock handler for GET requests
    @api.get("/getonly")
    def get_only_handler(request, response):
        response.body = b"GET only"

    # Simulate a POST request to a GET-only route
    environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/getonly"}
    start_response = lambda status, headers: None
    request = Request(environ)
    response = Response()

    # Call the API's `__call__` method (to simulate a request)
    api.__call__(environ, start_response)

    # Check that the response status code is 405 Method Not Allowed
    assert response.status_code == 405
    assert response.body == b"Method Not Allowed"
