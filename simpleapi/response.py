class Response:
    def __init__(
        self, status_code="404 Missing Not Found", message="Route not found!"
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.headers = []

    def as_wsgi(self, start_response):
        start_response(self.status_code, headers=self.headers)
        return [self.message.encode()]

    def send(
        self,
        message="",
        status_code="200 OK",
    ):
        if isinstance(message, str):
            self.message = message
        else:
            self.message = str(message)

        if isinstance(status_code, int):
            self.status_code = str(status_code)
        elif isinstance(status_code, str):
            self.status_code = status_code
        else:
            raise ValueError("Status codes have to be either int or string")
