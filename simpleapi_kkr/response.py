import json


class Response:
    STATUS_MESSAGES = {
        200: "OK",
        401: "Unauthorized",
        404: "Not Found",
        500: "Internal Server Error",
    }

    def __init__(self, status_code=404, message="Route not found!") -> None:
        self.status_code = status_code
        self._body = message
        self.headers = {"Content-Type": "text/plain"}  # Use a dictionary for headers

    @property
    def body(self):
        """Get the response body."""
        return self._body

    @body.setter
    def body(self, value):
        """Set the response body."""
        if isinstance(value, str):
            self._body = value
            self.set_header("Content-Type", "text/plain")
        elif isinstance(value, bytes):
            self._body = value
            self.set_header("Content-Type", "application/octet-stream")
        else:
            raise ValueError(
                "Body must be a string or bytes. Use `json()` for JSON data."
            )

    def json(self, data):
        """Set the response body as JSON."""
        if isinstance(data, (dict, list)):
            self._body = json.dumps(data)  # Serialize the data to JSON
            self.set_header("Content-Type", "application/json")
            self.status_code = 200  # Automatically set status to 200
        else:
            raise ValueError("JSON data must be a dictionary or list.")

    def set_header(self, key, value):
        """Set or update a response header."""
        self.headers[key] = value  # Directly update the dictionary

    def as_wsgi(self, start_response):
        """Prepare the response for WSGI format."""
        status_message = self.STATUS_MESSAGES.get(self.status_code, "Unknown Status")
        status_line = f"{self.status_code} {status_message}"
        start_response(
            status_line, list(self.headers.items())
        )  # Convert dictionary to list for WSGI

        # Ensure body is always bytes for WSGI
        return [self._body.encode() if isinstance(self._body, str) else self._body]
