from collections import defaultdict
from urllib.parse import parse_qs


class Request:
    def __init__(self, environ) -> None:
        self.environ = environ
        self.headers = self._parse_headers()
        self.queries = self._parse_query_string()

        # Set attributes for all keys in environ
        for key, value in self.environ.items():
            # Convert WSGI keys to a standard format for easier access
            setattr(self, key.replace(".", "_").lower(), value)

    def _parse_headers(self):
        """Extract headers from the WSGI environ."""
        headers = {}
        for key, value in self.environ.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_HEADER_NAME to Header-Name format
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        return headers

    def _parse_query_string(self):
        """Parse the query string into a dictionary using urllib."""
        queries = defaultdict(str)
        query_string = self.environ.get("QUERY_STRING", "")
        if query_string:
            parsed_queries = parse_qs(query_string)
            # Use `parse_qs` to ensure proper decoding
            for key, value in parsed_queries.items():
                queries[key] = value[
                    0
                ]  # Only take the first value if there are multiple
        return queries
