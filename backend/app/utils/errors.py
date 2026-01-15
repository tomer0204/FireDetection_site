class AppError(Exception):
    def __init__(self, message, status_code=500, code="INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

class BadRequest(AppError):
    def __init__(self, message="Bad request"):
        super().__init__(message, 400, "BAD_REQUEST")

class Unauthorized(AppError):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")

class Forbidden(AppError):
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403, "FORBIDDEN")

class Conflict(AppError):
    def __init__(self, message="Conflict"):
        super().__init__(message, 409, "CONFLICT")
