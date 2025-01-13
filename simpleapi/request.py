from collections import defaultdict


class Request:
    def __init__(self, environ) -> None:
        self.environ = environ
        self.queries = defaultdict()
        self.headers = self._parse_headers()

        # Set attributes for all keys in environ
        for key, value in self.environ.items():
            setattr(self, key.replace(".", "_").lower(), value)

        # Parse query string into queries dictionary
        if self.query_string:
            req_queries = self.query_string.split("&")
            for query in req_queries:
                query_key, query_val = query.split("=")
                self.queries[query_key] = query_val

    def _parse_headers(self):
        """Extract headers from the WSGI environ."""
        headers = {}
        for key, value in self.environ.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_HEADER_NAME to Header-Name format
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        return headers
