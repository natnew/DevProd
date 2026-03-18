class DevProdError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class NotFoundError(DevProdError):
    def __init__(self, message: str) -> None:
        super().__init__("not_found", message, 404)


class UnauthorizedError(DevProdError):
    def __init__(self, message: str) -> None:
        super().__init__("unauthorized", message, 401)


class RateLimitError(DevProdError):
    def __init__(self, message: str) -> None:
        super().__init__("rate_limited", message, 429)


class ServiceUnavailableError(DevProdError):
    def __init__(self, message: str) -> None:
        super().__init__("service_unavailable", message, 503)
