# Custom exceptions

class AppException(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR", status_code: int = 400, details: dict = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} not found: {identifier}", "NOT_FOUND", 404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, "FORBIDDEN", 403)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT", 409)


class RateLimitException(AppException):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, "RATE_LIMIT", 429, details)


class ExternalServiceException(AppException):
    def __init__(self, service: str, message: str, original_error: Exception = None):
        details = {"service": service}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(f"{service} error: {message}", "EXTERNAL_SERVICE_ERROR", 502, details)