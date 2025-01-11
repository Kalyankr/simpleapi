from collections import defaultdict


class Request:
    def __init__(self, environ) -> None:
        self.environ = environ
        self.queries = defaultdict()

        for key, value in self.environ.items():
            setattr(self, key.replace(".", "_").lower(), value)

        if self.query_string:
            req_queries = self.query_string.split("&")

            for query in req_queries:
                query_key, query_val = query.split("=")

                self.queries[query_key] = query_val
